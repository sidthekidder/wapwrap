import bentoml

from bentoml.io import Text, JSON
from transformers import pipeline

class PretrainedModelRunnable(bentoml.Runnable):
    SUPPORTED_RESOURCES = ("cpu",)
    SUPPORTS_CPU_MULTI_THREADING = True

    def __init__(self):
        self.sentiment_analyzer = pipeline(task="sentiment-analysis")

    @bentoml.Runnable.method(batchable=False)
    def __call__(self, input_text):
        return self.sentiment_analyzer(input_text)

runner = bentoml.Runner(PretrainedModelRunnable, name="sentiment_analyzer")

svc = bentoml.Service('wapwrap-sentimentservice', runners=[runner])

@svc.api(input=Text(), output=JSON())
async def sentiment(input_series: str) -> list:
    return await runner.async_run(input_series)
