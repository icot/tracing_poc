import asyncio
import aiozipkin as az

from functools import wraps

def atrace(name, tag, start, end, span_type="root", kind=az.CLIENT):
    def real_decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            zipkin_address = 'http://127.0.0.1:9412/api/v2/spans'
            endpoint = az.create_endpoint(
                "service", ipv4="127.0.0.1", port=8080)
            tracer = await az.create(zipkin_address, endpoint, sample_rate=1.0)
            with tracer.new_trace(sampled=True) as span:
                span.name(name)
                span.tag("span_type", span_type)
                span.kind(kind)
                span.annotate(start)
                output = function(*args, **kwargs)
                span.annotate(end)
            await tracer.close()
            return output
        return wrapper
    return real_decorator

async def run2():
    @atrace("test", "custom_tag", "comienzo", "final")
    def body():
        print("Executing")
        return 5
    await body()


async def run():
    # setup zipkin client
    zipkin_address = 'http://127.0.0.1:9412/api/v2/spans'
    endpoint = az.create_endpoint(
        "simple_service_old", ipv4="127.0.0.1", port=8081)
    tracer = await az.create(zipkin_address, endpoint, sample_rate=1.0)

    # create and setup new trace
    with tracer.new_trace(sampled=True) as span:
        # give a name for the span
        span.name("Slow SQL1")
        # tag with relevant information
        span.tag("span_type", "root")
        # indicate that this is client span
        span.kind(az.CLIENT)
        # make timestamp and name it with START SQL query
        span.annotate("START SQL SELECT * FROM")
        # imitate long SQL query
        await asyncio.sleep(0.1)
        # make other timestamp and name it "END SQL"
        span.annotate("END SQL")

    await tracer.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    #loop.run_until_complete(run())
    loop.run_until_complete(run2())
