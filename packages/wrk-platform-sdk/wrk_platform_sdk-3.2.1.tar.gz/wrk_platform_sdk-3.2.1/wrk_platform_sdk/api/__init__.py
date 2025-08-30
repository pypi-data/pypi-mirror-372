# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from wrk_platform_sdk.api.connected_accounts_api import ConnectedAccountsApi
    from wrk_platform_sdk.api.launch_activities_api import LaunchActivitiesApi
    from wrk_platform_sdk.api.launches_api import LaunchesApi
    from wrk_platform_sdk.api.webhooks_api import WebhooksApi
    from wrk_platform_sdk.api.wrk_action_resources_api import WrkActionResourcesApi
    from wrk_platform_sdk.api.wrkflows_api import WrkflowsApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from wrk_platform_sdk.api.connected_accounts_api import ConnectedAccountsApi
from wrk_platform_sdk.api.launch_activities_api import LaunchActivitiesApi
from wrk_platform_sdk.api.launches_api import LaunchesApi
from wrk_platform_sdk.api.webhooks_api import WebhooksApi
from wrk_platform_sdk.api.wrk_action_resources_api import WrkActionResourcesApi
from wrk_platform_sdk.api.wrkflows_api import WrkflowsApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
