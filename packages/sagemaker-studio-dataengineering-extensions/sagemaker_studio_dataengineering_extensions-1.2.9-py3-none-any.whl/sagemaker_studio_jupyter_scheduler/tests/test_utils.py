from sagemaker_studio_jupyter_scheduler.util.utils import generate_job_identifier


def test_generate_job_identifier():
    job_id = generate_job_identifier(
        name="@1l-sdsdfdsdfsd-kjf-2_/?12~`'k\"s'lj",
        notebook_name="!@#kskd23jksjdskdjsdnciususdfdhn12412((*&^",
    )
    assert job_id.startswith("1lsdsdfdsdfsdkjf2-kskd23jksjdskdjs-")
    assert len(job_id) == 63

    # TODO: find a way to test time and random id