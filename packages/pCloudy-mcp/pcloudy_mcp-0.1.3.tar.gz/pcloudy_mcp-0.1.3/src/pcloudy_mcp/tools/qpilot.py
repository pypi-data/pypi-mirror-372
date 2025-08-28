import traceback  # Make sure this import is at the top of your file
from urllib.parse import urlparse

from fastmcp.server.server import FastMCP

from ..api.browser_booking import BrowserBooking
from ..api.device_booking import DeviceBooking
from ..api.qpilot import QPilot
from ..errors.exception import McpToolError
from ..utils.tools_response_format import MCPResponseFormat

mcp_response = MCPResponseFormat()
qpilot = QPilot()
device = DeviceBooking()
browser_booking = BrowserBooking()


def qpilot_management(mcp_instance: FastMCP) -> None:
    """Register the QPilot management tools to run qpilot commands"""

    async def before_run_qpilot_steps(
        details_provided: bool,
        target_suite_name: None,
        target_case_name: None,
        target_project_name: None,
    ) -> dict:
        try:
            if not details_provided:
                # Get test case list
                testcases_response = await qpilot.get_testcase_list()
                owned_suites = (
                    testcases_response.get("data", {})
                    .get("testcases", {})
                    .get("owned", [])
                )
                if not owned_suites:
                    return {"error": "No owned test suites found."}

                # Get first test suite with at least one test case
                first_suite = next(
                    (suite for suite in owned_suites if suite.get("testcases")), None
                )
                if not first_suite:
                    return {"error": "No test cases found in owned test suites."}

                first_suite_id = first_suite.get("testSuiteId", "")
                first_suite_name = first_suite.get("testSuiteName", "")
                first_test_case = first_suite.get("testcases", [])[0]
                first_test_case_id = first_test_case.get("testCaseId", "")
                first_test_case_name = first_test_case.get("testCaseName", "")

                # Get project list
                project_response = await qpilot.get_project_list()
                projects = project_response.get("data", {}).get("owned", [])
                if not projects:
                    return {"error": "No owned projects found."}

                first_project = projects[0]
                first_project_id = first_project.get("projectId", "")
                first_project_name = first_project.get("projectName", "")

                # ✅ Return only the selected fields
                return {
                    "project_id": first_project_id,
                    "project_name": first_project_name,
                    "test_suite_id": first_suite_id,
                    "test_suite_name": first_suite_name,
                    "test_case_id": first_test_case_id,
                    "test_case_name": first_test_case_name,
                }

            else:
                # Get test case list
                testcases_response = await qpilot.get_testcase_list()
                test_suite_id = ""
                test_case_id = ""

                for suite in testcases_response["data"]["testcases"]["owned"]:
                    if suite["testSuiteName"] == target_suite_name:
                        for case in suite.get("testcases", []):
                            if case["testCaseName"] == target_case_name:
                                test_suite_id = suite["testSuiteId"]
                                test_case_id = case["testCaseId"]
                                break
                        if test_suite_id and test_case_id:
                            break

                if not test_suite_id or not test_case_id:
                    return {"error": "Matching test suite or test case not found."}

                # Get project list
                project_response = await qpilot.get_project_list()
                project_id = ""
                for project in project_response["data"]["owned"]:
                    if project["projectName"] == target_project_name:
                        project_id = project["projectId"]
                        break

                if not project_id:
                    return {"error": "Matching project not found."}

                return {
                    "project_id": project_id,
                    "project_name": target_project_name,
                    "test_suite_id": test_suite_id,
                    "test_suite_name": target_suite_name,
                    "test_case_id": test_case_id,
                    "test_case_name": target_case_name,
                }

        except Exception:
            return {"error": f"Exception occurred:\n{traceback.format_exc()}"}

    @mcp_instance.tool(
        name="get_qpilot_credits",
        description="Get available QPilot credits to run the qpilot features",
    )
    async def get_qpilot_credits() -> dict:
        try:
            credits = await qpilot.get_credit_balance()

            credits_left = (
                credits.get("result", {}).get("data", {}).get("creditsLeft", "Unknown")
            )

            return mcp_response.format(
                "text",
                f"✅ Available QPilot credits: {credits_left}",
                False,
            )

        except Exception as e:
            # logger.error("Exception : ", str(e))
            raise McpToolError("get_qpilot_credits", str(e)) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while fetching QPilot credits: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="get_qpilot_projects",
        description="Get list of QPilot owned projects",
    )
    async def get_qpilot_projects() -> dict:
        try:
            project_response = await qpilot.get_project_list()

            projects = project_response.get("data", {}).get("owned", [])

            if not projects:
                return mcp_response.format(
                    "text",
                    "⚠️ No owned QPilot projects found.",
                    False,
                )

            project_names = [
                f"🔹 {proj.get('projectName', 'Unknown')}" for proj in projects
            ]

            return mcp_response.format(
                "text",
                "✅ Owned QPilot Projects:\n\n" + "\n".join(project_names),
                False,
            )

        except Exception as e:
            raise McpToolError("get_qpilot_projects", str(e)) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while fetching QPilot projects: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="create_qpilot_project",
        description="This will create a new project for Qpilot run. User must specify project name in format: 'Project name : <Enter-Project-name>'",
    )
    async def create_qpilot_project(project_name: str) -> dict:
        try:
            if not project_name:
                return mcp_response.format(
                    "text",
                    "❌ Project name is required. Please specify in format: 'Project name : <Enter-Project-name>'",
                    True,
                )

            # Call create_project with the extracted name
            create_project_response = await qpilot.create_project(project_name)

            new_project_status = create_project_response.get("status")
            if new_project_status != "success":
                return mcp_response.format(
                    "text",
                    "❌ Error creating new project kindly connect to the pCloudy team",
                    True,
                )

            return mcp_response.format(
                "text",
                f"✅ Project '{project_name}' created successfully",
                False,
            )

        except Exception as e:
            raise McpToolError("create_qpilot_project", str(e)) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while creating QPilot project: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="get_qpilot_testsuites",
        description="Get list of QPilot owned testsuites",
    )
    async def get_qpilot_testsuites() -> dict:
        try:
            testsuites_response = await qpilot.get_testsuite_list()

            testsuites = (
                testsuites_response.get("data", {})
                .get("testSuites", {})
                .get("owned", [])
            )

            if not testsuites:
                return mcp_response.format(
                    "text",
                    "⚠️ No owned QPilot testsuites found.",
                    False,
                )

            testsuite_names = [
                f"🔹 {suite.get('testSuiteName', 'Unknown')}" for suite in testsuites
            ]

            return mcp_response.format(
                "text",
                "✅ Owned QPilot Test suites:\n\n" + "\n".join(testsuite_names),
                False,
            )

        except Exception as e:
            raise McpToolError("get_qpilot_testsuites", str(e)) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while fetching QPilot Test suites: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="create_qpilot_testsuite",
        description="This will create a new Test suite for Qpilot run. User must specify TEst suite name in format: 'Test suite name : <Enter-Test-suite-name>'",
    )
    async def create_qpilot_testsuite(testsuite_name: str) -> dict:
        try:

            if not testsuite_name:
                return mcp_response.format(
                    "text",
                    "❌ Test suite name is required",
                    True,
                )

            # Call create_testsuite with the extracted name
            create_testsuite_response = await qpilot.create_testsuite(testsuite_name)

            if "error" in create_testsuite_response:
                return mcp_response.format(
                    "text",
                    f"❌ Error creating new testsuite: {create_testsuite_response['error']}",
                    True,
                )

            new_testsuite = (
                create_testsuite_response.get("result").get("data").get("testsuiteid")
            )
            if not new_testsuite:
                return mcp_response.format(
                    "text",
                    "❌ Error creating new Test suite kindly connect to the pCloudy team",
                    True,
                )

            return mcp_response.format(
                "text",
                f"✅ Test suite '{testsuite_name}' created successfully",
                False,
            )

        except Exception as e:
            raise McpToolError("create_qpilot_testsuite", str(e)) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while creating QPilot Test suite: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="get_qpilot_testcases",
        description="Get list of QPilot test suites and their test cases",
    )
    async def get_qpilot_testcases() -> dict:
        try:
            testcases_response = await qpilot.get_testcase_list()

            owned_suites = (
                testcases_response.get("data", {}).get("testcases", {}).get("owned", [])
            )

            if not owned_suites:
                return mcp_response.format(
                    "text",
                    "⚠️ No owned QPilot testcases found.",
                    False,
                )

            all_testcases = []

            for suite in owned_suites:
                suite_name = suite.get("testSuiteName", "Unnamed Suite")
                testcases = suite.get("testcases", [])
                for case in testcases:
                    case_name = case.get("testCaseName", "Unnamed Test Case")
                    all_testcases.append(f"🔹 {case_name} (Suite: {suite_name})")

            if not all_testcases:
                return mcp_response.format(
                    "text",
                    "⚠️ No test cases found inside owned suites.",
                    False,
                )

            return mcp_response.format(
                "text",
                "✅ QPilot Test Cases:\n\n" + "\n".join(all_testcases),
                False,
            )

        except Exception as e:
            raise McpToolError("get_qpilot_testcases", str(e)) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while fetching QPilot Test suites: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="create_qpilot_testcase",
        description="Create a new test case in QPilot. Requires test suite name and test case name in format: 'Test suite name : <Enter-TestSuite-name>' and 'Test case name : <Enter-TestCase-name>'",
    )
    async def create_qpilot_testcase(
        suite_name: str,
        case_name: str,
        platform: str = None,
    ) -> dict:
        try:

            # Validate required parameters
            missing_params = []
            if not suite_name:
                missing_params.append("Test suite name")
            if not case_name:
                missing_params.append("Test case name")
            if not platform:
                missing_params.append("Platform")

            if missing_params:
                return mcp_response.format(
                    "text",
                    f"❌ Missing required parameters: {', '.join(missing_params)}",
                    True,
                )

            # Validate platform value
            if platform not in ["android", "ios", "web"]:
                return mcp_response.format(
                    "text",
                    f"❌ Invalid platform '{platform}'. Platform must be either ('android' ,'ios') for devices and 'web' for browsers.",
                    False,
                )

            # Get test suite list to find the suite ID
            testsuites_response = await qpilot.get_testsuite_list()

            # Find the test suite ID
            testsuites = (
                testsuites_response.get("data", {})
                .get("testSuites", {})
                .get("owned", [])
            )
            suite_id = None

            for suite in testsuites:
                if suite.get("testSuiteName") == suite_name:
                    suite_id = suite.get("testSuiteId")
                    break

            if not suite_id:
                return mcp_response.format(
                    "text",
                    f"❌ Test suite '{suite_name}' not found. Please check the test suite name or create it first.",
                    True,
                )

            # Create the test case with platform parameter
            create_testcase_response = await qpilot.create_testcase(
                suite_id, case_name, platform
            )

            new_testcase = (
                create_testcase_response.get("result").get("data").get("testcaseid")
            )

            if not new_testcase:
                return mcp_response.format(
                    "text",
                    "❌ Error creating test case. Please contact the pCloudy team.",
                    True,
                )

            return mcp_response.format(
                "text",
                f"✅ Test case '{case_name}' created successfully in test suite '{suite_name}' for platform '{platform}'",
                False,
            )

        except Exception as e:
            raise McpToolError("create_qpilot_testcase", str(e)) from e
            return mcp_response.format(
                "text",
                f"❌ Exception while creating QPilot test case: {str(e)}",
                True,
            )

    @mcp_instance.tool(
        name="qpilot_run_steps",
        description="Execute natural language steps using QPilot automation",
    )
    async def qpilot_run_steps(
        rid: int,
        platform: str,
        app_name: str = None,
        app_package: str = None,
        app_activity: str = None,
        bundle_id: str = None,
        project: str = None,
        test_suite: str = None,
        test_case: str = None,
        steps: str = None,
    ) -> dict:
        try:
            credits = await qpilot.get_credit_balance()
            credits_left = (
                credits.get("result", {}).get("data", {}).get("creditsLeft", "Unknown")
            )
            if isinstance(credits_left, (int, float)) and credits_left <= 0:
                return mcp_response.format(
                    "text",
                    f"❌ Not able to proceed: Insufficient qpilot credits => '{credits_left}' kindly contact support",
                    True,
                )
            if not rid:
                return mcp_response.format(
                    "text",
                    "❌ No device booked. Not able to find any rid Please book a device first using the 'book_device' tool.",
                    True,
                )

            if not platform:
                return mcp_response.format(
                    "text",
                    "❌ Platform information missing. Please provide the platform.",
                    True,
                )

            # Check if user provided app and QPilot details
            app_fields = [app_name, app_package, app_activity, bundle_id]
            input_has_app_fields = any(field and field.strip() for field in app_fields)

            qpilot_fields = [project, test_suite, test_case]
            input_has_qpilot_fields = any(
                field and field.strip() for field in qpilot_fields
            )
            if input_has_app_fields:

                # Get QPilot mandatory fields
                qpilot_mandatory_fields = await before_run_qpilot_steps(
                    details_provided=input_has_qpilot_fields,
                    target_project_name=project,
                    target_suite_name=test_suite,
                    target_case_name=test_case,
                )

                if "error" in qpilot_mandatory_fields:
                    return mcp_response.format(
                        "text",
                        f"❌ QPilot configuration error: {qpilot_mandatory_fields['error']}",
                        True,
                    )

                test_case_name = qpilot_mandatory_fields.get("test_case_name", "")
                test_suite_name = qpilot_mandatory_fields.get("test_suite_name", "")
                project_name = qpilot_mandatory_fields.get("project_name", "")

                if not all([test_case_name, test_suite_name, project_name]):
                    return mcp_response.format(
                        "text",
                        "❌ QPilot configuration incomplete. Could not find or create the specified project/testsuite/testcase.",
                        True,
                    )

                # Validate app details based on platform
                if platform.lower() == "android":
                    missing_fields = [
                        name
                        for name, val in {
                            "app name": app_name,
                            "app package": app_package,
                            "app activity": app_activity,
                        }.items()
                        if not val
                    ]
                    if missing_fields:
                        return mcp_response.format(
                            "text",
                            mcp_response.qpilot_missing_app_details_response(
                                "android", missing_fields
                            ),
                            True,
                        )
                else:  # iOS
                    missing_fields = [
                        name
                        for name, val in {
                            "app name": app_name,
                            "bundle id": bundle_id,
                        }.items()
                        if not val
                    ]
                    if missing_fields:
                        return mcp_response.format(
                            "text",
                            mcp_response.qpilot_missing_app_details_response(
                                "ios", missing_fields
                            ),
                            True,
                        )
                    # Use bundle_id as app_package for iOS
                    app_package = bundle_id
                    app_activity = None

                if not steps or len(steps.strip()) < 5:
                    return mcp_response.format(
                        "text",
                        mcp_response.qpilot_no_steps_error_reponse(
                            app_name, app_package, app_activity, platform
                        ),
                        True,
                    )

                # Prepare payload
                payload = {
                    "rid": rid,
                    "description": f"mcp-test-{test_case_name}",
                    "testId": qpilot_mandatory_fields["test_case_id"],
                    "suiteId": qpilot_mandatory_fields["test_suite_id"],
                    "appPackage": app_package,
                    "appName": app_name,
                    "appActivity": (
                        app_activity if platform.lower() == "android" else ""
                    ),
                    "steps": steps,
                    "projectId": qpilot_mandatory_fields["project_id"],
                    "platform": platform,
                    "testdata": {},
                }

                # Run QPilot code generation
                execution_result = await qpilot.generate_code(
                    rid=payload["rid"],
                    app_name=payload["appName"],
                    description=payload["description"],
                    test_id=payload["testId"],
                    suite_id=payload["suiteId"],
                    app_package=payload["appPackage"],
                    app_activity=payload["appActivity"],
                    steps=payload["steps"],
                    project_id=payload["projectId"],
                    platform=payload["platform"],
                )

                if "error" in execution_result:
                    return mcp_response.format(
                        "text",
                        f"❌ Error executing QPilot steps: {execution_result['error']}",
                        True,
                    )
                get_live_view_url = await device.get_live_view_url(rid)
                result = get_live_view_url.get("result", {})
                url = (
                    result.get("URL", "")
                    if result.get("code") == 200
                    else "url not available"
                )
                return mcp_response.format(
                    "json",
                    {
                        "message": "✅ QPilot steps execution intiated successfully",
                        "qpilot_config_used": {
                            "project": project_name,
                            "suite": test_suite_name,
                            "testcase": test_case_name,
                            "description": payload["description"],
                            "details_provided_by_user": input_has_qpilot_fields,
                            "user_specified": {
                                "project": (
                                    project if input_has_qpilot_fields else "default"
                                ),
                                "suite": (
                                    test_suite if input_has_qpilot_fields else "default"
                                ),
                                "testcase": (
                                    test_case if input_has_qpilot_fields else "default"
                                ),
                            },
                            "live_view": url,
                        },
                    },
                    False,
                )

            else:
                # No app details in input - ask for them with examples
                if platform.lower() == "android":
                    return mcp_response.format(
                        "text",
                        mcp_response.qpilot_no_app_details_reponse("android"),
                        True,
                    )
                else:  # iOS
                    return mcp_response.format(
                        "text",
                        mcp_response.qpilot_no_app_details_reponse("ios"),
                        True,
                    )

        except Exception as e:
            raise McpToolError("qpilot_run_steps", str(e)) from e
            return mcp_response.format(
                "text", f"❌ Error executing QPilot steps: {str(e)}", True
            )

    @mcp_instance.tool(
        name="qpilot_run_steps_browser",
        description="Execute natural language steps using QPilot automation",
    )
    async def qpilot_run_steps_browser(
        feature_name: str = None,
        project: str = None,
        test_suite: str = None,
        test_case: str = None,
        steps: str = None,
        url: str = None,
        vm_id: str = None,
        browser: str = None,
        browser_version: str = None,
        os: str = None,
        os_version: str = None,
    ) -> dict:
        try:
            credits = await qpilot.get_credit_balance()
            credits_left = (
                credits.get("result", {}).get("data", {}).get("creditsLeft", "Unknown")
            )
            if isinstance(credits_left, (int, float)) and credits_left <= 0:
                return mcp_response.format(
                    "text",
                    f"❌ Not able to proceed: Insufficient qpilot credits => '{credits_left}' kindly contact support",
                    True,
                )
            if not vm_id or not browser or not browser_version:
                return mcp_response.format(
                    "text",
                    "❌ No browser booked. Not able to find any vm_id , Browser , Browser Version. Please book a browser first using the 'book_browser' tool.",
                    True,
                )

            if not url:
                return mcp_response.format(
                    "text",
                    "❌ URL information missing. Please provide the URL.",
                    True,
                )

            qpilot_fields = [project, test_suite, test_case]
            input_has_qpilot_fields = any(
                field and field.strip() for field in qpilot_fields
            )
            # Get QPilot mandatory fields
            qpilot_mandatory_fields = await before_run_qpilot_steps(
                details_provided=input_has_qpilot_fields,
                target_project_name=project,
                target_suite_name=test_suite,
                target_case_name=test_case,
            )

            if "error" in qpilot_mandatory_fields:
                return mcp_response.format(
                    "text",
                    f"❌ QPilot configuration error: {qpilot_mandatory_fields['error']}",
                    True,
                )
            test_case_name = qpilot_mandatory_fields.get("test_case_name", "")
            test_suite_name = qpilot_mandatory_fields.get("test_suite_name", "")
            project_name = qpilot_mandatory_fields.get("project_name", "")
            if not all([test_case_name, test_suite_name, project_name]):
                return mcp_response.format(
                    "text",
                    "❌ QPilot configuration incomplete. Could not find or create the specified project/testsuite/testcase.",
                    True,
                )
            if not steps or len(steps.strip()) < 5:
                return mcp_response.format(
                    "text",
                    mcp_response.qpilot_no_steps_error_reponse_browser(),
                    True,
                )
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname

            # Prepare payload
            payload = {
                "vmId": vm_id,
                "featureName": feature_name or f"{hostname} feature",
                "testId": qpilot_mandatory_fields["test_case_id"],
                "suiteId": qpilot_mandatory_fields["test_suite_id"],
                "steps": steps,
                "projectId": qpilot_mandatory_fields["project_id"],
                "url": url,
                "browser": browser,
                "browserVersion": browser_version,
            }
            # Run QPilot code generation
            execution_result = await qpilot.generate_code_browser(
                feature_name=payload["featureName"],
                test_id=payload["testId"],
                suite_id=payload["suiteId"],
                steps=payload["steps"],
                vm_id=payload["vmId"],
                browser=payload["browser"],
                browser_version=payload["browserVersion"],
                url=payload["url"],
            )
            if "error" in execution_result:
                return mcp_response.format(
                    "text",
                    f"❌ Error executing QPilot steps: {execution_result['error']}",
                    True,
                )
            get_live_view_url = "Need OS and OS Version for live view url"
            if os and os_version:
                get_live_view_url = await browser_booking.view_live_url(
                    vm_id, os, os_version, browser, browser_version
                )
            return mcp_response.format(
                "json",
                {
                    "message": "✅ QPilot steps execution intiated successfully",
                    "qpilot_config_used": {
                        "suite": test_suite_name,
                        "testcase": test_case_name,
                        "feature": payload["featureName"],
                        "details_provided_by_user": input_has_qpilot_fields,
                        "user_specified": {
                            "suite": (
                                test_suite if input_has_qpilot_fields else "default"
                            ),
                            "testcase": (
                                test_case if input_has_qpilot_fields else "default"
                            ),
                        },
                        "live_view": get_live_view_url,
                    },
                },
                False,
            )

        except Exception as e:
            raise McpToolError("qpilot_run_steps_browser", str(e)) from e
            return mcp_response.format(
                "text", f"❌ Error executing QPilot steps: {str(e)}", True
            )
