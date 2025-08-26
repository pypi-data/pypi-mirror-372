import functools
import io
import os

from concurrent.futures import ProcessPoolExecutor, Future
from contextlib import redirect_stderr, redirect_stdout, nullcontext
from dataclasses import dataclass, field
from enum import Enum, auto
from random import choice
from sqlalchemy import create_engine, select, ForeignKey, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass, Session, relationship
from typing import Dict, Any, Optional, List, Self, Set, Tuple

from cyst.api.environment.environment import Environment
from cyst.api.utils.counter import Counter

from aica_challenge_1.package_manager import PackageManager
from aica_challenge_1.scenario_manager import ScenarioManager, ScenarioVariant
from aica_challenge_1.launcher import launch_simulation
from aica_challenge_1.execution_structures import Episode, DBEpisode, DBRun, RunStatus, RunSpecification, Run, Base, \
    DBRunParameter, DBRunSpecification


class ExecutionManager:
    """
    The execution manager retrieves run specifications and takes care of run executions.
    """
    def __init__(self, package_manager: PackageManager, scenario_manager: ScenarioManager):
        self._package_manager = package_manager
        self._scenario_manager = scenario_manager
        self._run_specifications: Dict[str, RunSpecification] = {}
        self._run_specifications_by_id: Dict[id, RunSpecification] = {}

        self._db = create_engine("sqlite+pysqlite:///aica_challenge.db")
        Base.metadata.create_all(self._db)

        with Session(self._db) as session:
            for obj in session.execute(select(DBRunSpecification)).scalars():
                spec = RunSpecification.from_db_spec(obj)
                self._run_specifications[obj.name] = spec
                self._run_specifications_by_id[obj.id] = spec

            parameters: Dict[int, List[DBRunParameter]] = {}
            for obj in session.execute(select(DBRunParameter)).scalars():
                if not obj.run_id in parameters:
                    parameters[obj.run_id] = []
                parameters[obj.run_id].append(obj)

            for spec in self._run_specifications.values():
                if spec.db_id in parameters:
                    for param in parameters[spec.db_id]:
                        spec.parameters[param.key] = param.value

        self._runs: Dict[int, Run] = {}

    def list_run_specifications(self) -> List[str]:
        """
        Provides a list of run names that are available for execution.

        :return: A list of run names.
        """
        return sorted(self._run_specifications.keys())

    def get_run_specification(self, name: str) -> Optional[RunSpecification]:
        """
        Attempts to retrieve a run specification by name.

        :param name: A name of the specification.

        :return: A run specification if it exists for a given name, or None otherwise.
        """
        return self._run_specifications.get(name, None)

    def set_run_specification(self, specification: RunSpecification, old_specification: Optional[RunSpecification] = None) -> None:
        """
        Saves a run specification to the database.

        :param specification: A specification that should be saved.
        :param old_specification: If provided, this specification will be overwritten by the other specification
        """
        if old_specification and old_specification.name and old_specification.name != specification.name:
            del self._run_specifications[str(old_specification.name)]

        self._run_specifications[specification.name] = specification

        with Session(self._db) as session:
            db_obj = None
            if specification.db_id != -1:
                db_obj = session.execute(select(DBRunSpecification).where(DBRunSpecification.id==specification.db_id)).scalar_one()
                db_obj.replace(specification)
            else:
                db_obj = DBRunSpecification.copy(specification)

            session.add(db_obj)
            session.flush()

            if specification.db_id == -1:
                specification.db_id = db_obj.id

            specification_keys = set(specification.parameters.keys())
            db_keys = set()

            for obj in session.execute(select(DBRunParameter).where(DBRunParameter.run_id==db_obj.id)).scalars():
                # Key was deleted
                if obj.key not in specification.parameters:
                    session.execute(delete(DBRunParameter).where(DBRunParameter.id == obj.id))
                else:
                    db_keys.add(obj.key)
                    obj.value = specification.parameters[obj.key]
                    session.add(obj)

            new_keys = specification_keys - db_keys
            for key in new_keys:
                session.add(DBRunParameter(run_id=db_obj.id, key=key, value=specification.parameters[key]))

            session.commit()

    def save_run_information(self, run: Run) -> None:
        with Session(self._db, expire_on_commit=False) as session:
            stmt = select(DBRun).where(DBRun.id == run.id)
            run_db: DBRun = session.scalars(stmt).one()

            details = f"Successfull episodes: {sorted(list(run.successful))}, failed episodes: {sorted(list(run.error))}"

            run.detail = details
            run_db.details = details

            # We set status to finished whenever there was at elast one successful episode
            status = RunStatus.FINISHED if run.successful else RunStatus.ERROR
            run.status = status
            run_db.status = str(status)

            session.commit()

    def get_run(self, run_id: int) -> Run:
        """
        Gets the information about a specific run.

        :param run_id: An ID of the run to get.

        :return: A run information.
        """
        return self._runs[run_id]

    def get_runs(self) -> List[Tuple[int, RunStatus]]:
        """
        Gets the IDs and statuses of all runs executed in the challenge instance.

        :return: Tuple containing the ID [0] and status [1] for each run.
        """
        result = []
        for k in sorted(self._runs.keys()):
            r = self._runs[k]
            result.append((k, self._runs[k].status))
        return result

    def execution_callback(self, episode_number: int, future: Future):
        if future.exception():
            print(f"The episode {episode_number} has been terminated.")
            return

        e: Episode = future.result()
        run = self._runs[e.run]
        run.episodes[episode_number] = e
        run.running.remove(episode_number)
        if e.status == RunStatus.FINISHED:
            run.successful.add(episode_number)
        else:
            run.error.add(episode_number)

        if not run.running:
            self.save_run_information(run)

    def execute(self, specification: RunSpecification | str, single_process=False) -> None:
        """
        Executes a run.

        :param specification: Either a RunSpecification object or a name of a run specification that is stored in
            the database.
        :param single_process: If set to True, it will execute only one run at a time (regardless of the run
            specification) and it will display the stdout and stderr. If set to False, it will execute each run in a
            new process (even if the run specification says no parallel runs) and stdout and stderr are hidden and
            stored in the database.
        """
        if isinstance(specification, str):
            spec_name = specification
            specification = self._run_specifications.get(specification, None)
            if not specification:
                raise ValueError(f"Run with the name '{spec_name}' not available in the system.")

        with Session(self._db) as session:
            """
            # Refresh run specification
            specification = session.get(DBRunSpecification, specification.db_id)

            if not specification:
               raise ValueError(f"There was an error extracting run specification from the database")

            parameters = []
            for obj in session.execute(select(DBRunParameter).where(DBRunParameter.run_id==specification.id)).scalars():
                parameters.append(obj)
            """

            run = Run(specification)

            db_specification = session.get(DBRunSpecification, specification.db_id)
            db_run = DBRun(
                status=str(RunStatus.INIT),
                details="",
                episodes=[],
                specification_id=specification.db_id,
                specification=db_specification
            )

            session.add(db_run)
            session.flush()

            if not specification.name:
                run.status = RunStatus.ERROR
                run.detail = "Run specification must have a name."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            if specification.agent_name not in self._package_manager.list_installed_agents():
                run.status = RunStatus.ERROR
                run.detail = f"Chosen agent '{specification.agent_name}' not installed in the system."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            scenario_name = specification.scenario
            scenario = self._scenario_manager.get_scenario(scenario_name)

            if scenario_name == "Random":
                scenarios = self._scenario_manager.get_scenarios()
                if not scenarios:
                    run.status = RunStatus.ERROR
                    run.detail = "No scenarios installed in the system. Cannot choose a random one."
                    db_run.status = str(RunStatus.ERROR)
                    db_run.details = run.detail
                    session.commit()
                    return
                s = choice(scenarios)
                scenario_name = s.short_path
                scenario = s

            if not scenario:
                run.status = RunStatus.ERROR
                run.detail = f"Chosen scenario '{specification.scenario}' not available."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            variant_id = specification.variant
            variants = scenario.variants

            if variant_id == -1:
                if not variants:
                    run.status = RunStatus.ERROR
                    run.detail = f"No variants of the scenario '{scenario_name}' exist. Cannot choose a random one."
                    db_run.status = str(RunStatus.ERROR)
                    db_run.details = run.detail
                    session.commit()
                    return
                variant_id = choice(list(variants.keys()))

            elif variant_id not in variants:
                run.status = RunStatus.ERROR
                run.detail = f"Variant '{variant_id}' of the scenario '{scenario_name}' is not available in the system."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            scenario_variant = self._scenario_manager.get_scenario(scenario_name).variants[variant_id]

            run.id = db_run.id
            self._runs[run.id] = run

            run.status = RunStatus.RUNNING
            db_run.status = str(RunStatus.RUNNING)

            session.commit()

        # Add scenario-level parameters unless overwritten by the user
        for key, value in scenario.parameters.items():
            if key not in specification.parameters:
                specification.parameters[key] = value

        if not single_process:
            run.executor = ProcessPoolExecutor(max_workers=specification.max_parallel)

            for e in range(specification.max_episodes):
                future: Future = run.executor.submit(launch_simulation, run.id, e, scenario_variant,
                                                     specification.agent_name, specification.max_time,
                                                     specification.max_actions, specification.parameters)
                future.add_done_callback(functools.partial(self.execution_callback, e))
                run.running.add(e)
        else:
            for e in range(specification.max_episodes):
                ep = launch_simulation(run.id, e, scenario_variant, specification.agent_name, specification.max_time,
                                       specification.max_actions, specification.parameters, supress_output=False)

                if ep.status == RunStatus.FINISHED:
                    run.successful.add(e)
                else:
                    run.error.add(e)

            self.save_run_information(run)
