import json
import typing as t
from datetime import datetime, timedelta

from prefect import flow, get_run_logger
from punchbowl.level1.stray_light import estimate_stray_light

from punchpipe import __version__
from punchpipe.control.db import File, Flow
from punchpipe.control.processor import generic_process_flow_logic
from punchpipe.control.scheduler import generic_scheduler_flow_logic
from punchpipe.control.util import get_database_session, load_pipeline_configuration
from punchpipe.flows.util import file_name_to_full_path


def construct_stray_light_check_for_inputs(session,
                                           pipeline_config: dict,
                                           reference_time: datetime,
                                           reference_file: File):
    logger = get_run_logger()

    min_files_per_half = pipeline_config['flows']['construct_stray_light']['min_files_per_half']
    max_files_per_half = pipeline_config['flows']['construct_stray_light']['max_files_per_half']
    max_hours_per_half = pipeline_config['flows']['construct_stray_light']['max_hours_per_half']
    t_start = reference_time - timedelta(hours=max_hours_per_half)
    t_end = reference_time + timedelta(hours=max_hours_per_half)
    L0_impossible_after_days = pipeline_config['flows']['construct_stray_light']['new_L0_impossible_after_days']
    more_L0_impossible = datetime.now() - t_end > timedelta(days=L0_impossible_after_days)

    file_type_mapping = {"SR": "XR", "SM": "XM", "SZ": "XZ", "SP": "XP"}
    target_file_type = file_type_mapping[reference_file.file_type]
    L0_type_mapping = {"SR": "CR", "SM": "PM", "SZ": "PZ", "SP": "PP"}
    L0_target_file_type = L0_type_mapping[reference_file.file_type]

    base_query = (session.query(File)
                  .filter(File.state.in_(["created", "progressed"]))
                  .filter(File.observatory == reference_file.observatory)
                  .filter(~File.outlier)
                  )

    first_half_inputs = (base_query
                         .filter(File.date_obs >= t_start)
                         .filter(File.date_obs <= reference_time)
                         .filter(File.file_type == target_file_type)
                         .filter(File.level == "1")
                         .order_by(File.date_obs.desc())
                         .limit(max_files_per_half).all())

    second_half_inputs = (base_query
                          .filter(File.date_obs >= reference_time)
                          .filter(File.date_obs <= t_end)
                          .filter(File.file_type == target_file_type)
                          .filter(File.level == "1")
                          .order_by(File.date_obs.asc())
                          .limit(max_files_per_half).all())

    first_half_L0s = (base_query
                      .filter(File.date_obs >= t_start)
                      .filter(File.date_obs <= reference_time)
                      .filter(File.file_type == L0_target_file_type)
                      .filter(File.level == "0")
                      .order_by(File.date_obs.desc())
                      .limit(max_files_per_half).all())

    second_half_L0s = (base_query
                       .filter(File.date_obs >= reference_time)
                       .filter(File.date_obs <= t_end)
                       .filter(File.file_type == L0_target_file_type)
                       .filter(File.level == "0")
                       .order_by(File.date_obs.asc())
                       .limit(max_files_per_half).all())

    # Allow 5% of the L0s to not be processed, in case a few fail
    all_inputs_ready = (len(first_half_inputs) >= 0.95 * len(first_half_L0s)
                        and len(second_half_inputs) >= 0.95 * len(second_half_L0s))
    enough_L1s = len(first_half_inputs) > min_files_per_half and len(second_half_inputs) > min_files_per_half
    max_L1s = len(first_half_inputs) == max_files_per_half and len(second_half_inputs) == max_files_per_half

    produce = False
    if more_L0_impossible:
        if len(first_half_L0s) < min_files_per_half or len(second_half_L0s) < min_files_per_half:
            reference_file.state = "impossible"
            # Record who deemed this to be impossible
            reference_file.file_version = pipeline_config["file_version"]
            reference_file.software_version = __version__
            reference_file.date_created = datetime.now()
        elif all_inputs_ready and enough_L1s:
            n = min(len(first_half_inputs), len(second_half_inputs))
            first_half_inputs = first_half_inputs[:n]
            second_half_inputs = second_half_inputs[:n]
            produce = True
    elif max_L1s:
        produce = True

    if produce:
        all_ready_files = first_half_inputs + second_half_inputs

        logger.info(f"{len(all_ready_files)} Level 1 {target_file_type}{reference_file.observatory} files will be used "
                     "for stray light estimation.")
        return [f.file_id for f in all_ready_files]
    return []


def construct_stray_light_flow_info(level1_files: list[File],
                                    level1_stray_light_files: File,
                                    pipeline_config: dict,
                                    reference_time: datetime,
                                    file_type: str,
                                    spacecraft: str,
                                    session=None):
    flow_type = "construct_stray_light"
    state = "planned"
    creation_time = datetime.now()
    priority = pipeline_config["flows"][flow_type]["priority"]["initial"]
    call_data = json.dumps(
        {
            "filepaths": [level1_file.filename() for level1_file in level1_files],
            "reference_time": reference_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    return Flow(
        flow_type=flow_type,
        state=state,
        flow_level="1",
        creation_time=creation_time,
        priority=priority,
        call_data=call_data,
    )


def construct_stray_light_file_info(level1_files: t.List[File],
                                    pipeline_config: dict,
                                    reference_time: datetime,
                                    file_type: str,
                                    spacecraft: str) -> t.List[File]:
    date_obses = [f.date_obs for f in level1_files]
    return [File(
                level="1",
                file_type=file_type,
                observatory=spacecraft,
                polarization=level1_files[0].polarization,
                file_version=pipeline_config["file_version"],
                software_version=__version__,
                date_obs=reference_time,
                date_beg=min(date_obses),
                date_end=max(date_obses),
                state="planned",
            ),]

@flow
def construct_stray_light_scheduler_flow(pipeline_config_path=None, session=None, reference_time: datetime | None = None):
    session = get_database_session()
    pipeline_config = load_pipeline_configuration(pipeline_config_path)
    logger = get_run_logger()

    if not pipeline_config["flows"]['construct_stray_light'].get("enabled", True):
        logger.info("Flow 'construct_stray_light' is not enabled---halting scheduler")
        return 0

    max_flows = 2 * pipeline_config['flows']['construct_stray_light'].get('concurrency_limit', 1000)
    existing_flows = (session.query(Flow)
                      .where(Flow.flow_type == 'construct_stray_light')
                      .where(Flow.state.in_(["planned", "launched", "running"])).count())

    flows_to_schedule = max_flows - existing_flows
    if flows_to_schedule <= 0:
        logger.info("Our maximum flow count has been reached; halting")
        return
    else:
        logger.info(f"Will schedule up to {flows_to_schedule} flows")

    existing_models = (session.query(File)
                       .filter(File.level == "1")
                       .filter(File.file_type.in_(['SR', 'SM', 'SZ', 'SP']))
                       .all())
    logger.info(f"There are {len(existing_models)} model records in the DB")

    existing_models = {(model.file_type, model.observatory, model.date_obs): model for model in existing_models}
    t0 = datetime.strptime(pipeline_config['flows']['construct_stray_light']['t0'], "%Y-%m-%d %H:%M:%S")
    increment = timedelta(hours=float(pipeline_config['flows']['construct_stray_light']['model_spacing_hours']))
    n = 0
    models_to_try_creating = []
    # I'm sure there's a better way to do this, but let's step forward by increments to the present, and then we'll work
    # backwards back to t0, so that we prioritize the stray light models that QuickPUNCH uses
    while t0 + n * increment < datetime.now():
        n += 1

    for i in range(n, -1, -1):
        t = t0 + i * increment
        for model_type in ['SR', 'SM', 'SZ', 'SP']:
            for observatory in ['1', '2', '3', '4']:
                key = (model_type, observatory, t)
                model = existing_models.get(key, None)
                if model is None:
                    new_model = File(state='waiting',
                                     level='1',
                                     file_type=model_type,
                                     observatory=observatory,
                                     polarization='C' if model_type[1] == 'R' else model_type[1],
                                     date_obs=t,
                                     date_created=datetime.now(),
                                     file_version=pipeline_config["file_version"],
                                     software_version=__version__)
                    session.add(new_model)
                    models_to_try_creating.append(new_model)
                elif model.state == 'waiting':
                    models_to_try_creating.append(model)

    logger.info(f"There are {len(models_to_try_creating)} waiting models")

    to_schedule = []
    for model in models_to_try_creating:
        ready_files = construct_stray_light_check_for_inputs(
            session, pipeline_config, model.date_obs, model)
        if ready_files:
            to_schedule.append((model, ready_files))
            logger.info(f"Will schedule {model.file_type} at {model.date_obs}")
            if len(to_schedule) == flows_to_schedule:
                break

    if len(to_schedule):
        for model, input_files in to_schedule:
            # Clear the placeholder model entry---it'll be regenerated in the scheduling flow
            args_dictionary = {"file_type": model.file_type, "spacecraft": model.observatory}
            dateobs = model.date_obs
            session.delete(model)
            generic_scheduler_flow_logic(
                lambda *args, **kwargs: [input_files],
                construct_stray_light_file_info,
                construct_stray_light_flow_info,
                pipeline_config,
                update_input_file_state=False,
                session=session,
                args_dictionary=args_dictionary,
                cap_planned_flows=False,
                reference_time=dateobs,
            )

        logger.info(f"Scheduled {len(to_schedule)} models")
    session.commit()


def construct_stray_light_call_data_processor(call_data: dict, pipeline_config, session) -> dict:
    # Prepend the directory path to each input file
    call_data['filepaths'] = file_name_to_full_path(call_data['filepaths'], pipeline_config['root'])
    call_data['num_workers'] = 32
    return call_data

@flow
def construct_stray_light_process_flow(flow_id: int, pipeline_config_path=None, session=None):
    generic_process_flow_logic(flow_id, estimate_stray_light, pipeline_config_path, session=session,
                               call_data_processor=construct_stray_light_call_data_processor)
