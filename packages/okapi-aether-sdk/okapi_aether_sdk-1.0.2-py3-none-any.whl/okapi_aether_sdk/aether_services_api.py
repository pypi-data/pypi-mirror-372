from typing import Optional

from okapi_aether_sdk.aether_api import AetherApi


class AetherServicesApi(AetherApi):
    """
    AetherServicesApi class that provides methods for interacting
    with service-related endpoints of the Aether API.

    This class inherits from AetherApi and handles specific operations
    related to ephemerides, risk estimation, orbit determination, and
    other services offered by the Aether API.
    """

    def add_ephemerides(self, ephemeris_to_add: dict, timeout: float = 20.0) -> str:
        """
        Initiates the addition of ephemerides.

        :param ephemeris_to_add: A dictionary containing the ephemeris data to add.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the ephemeris addition process.
        """
        return self.get_request_id("add-ephemerides/requests", ephemeris_to_add, timeout)

    def get_add_ephemerides_results(
        self,
        request_id: str,
        result_format: str,
        result_part_id: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        timeout: float = 20.0,
    ) -> dict:
        """
        Retrieves the results of the add ephemerides request.

        :param request_id: The ID of the request for which to retrieve results.
        :param result_format: The format of the results ('simple' or 'oem').
        :param result_part_id: Optional part ID for retrieving a specific portion of the result.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the add ephemerides request.
        :raises ValueError: If the format provided is invalid.
        """
        # Validate the format parameter
        valid_formats = {"simple", "oem"}
        if result_format not in valid_formats:
            raise ValueError(
                f"Invalid format '{result_format}'. Expected one of: {', '.join(valid_formats)}."
            )

        # Construct the URL for the request
        if result_part_id is not None:
            result_url = f"add-ephemerides/results/{request_id}/{result_format}/{result_part_id}"
        else:
            result_url = f"add-ephemerides/results/{request_id}/{result_format}"

        # Wait for and return the request result
        return self.wait_for_request_result(result_url, max_retries, retry_delay, timeout)

    def correlate_observation(self, target_observation: dict, timeout: float = 20.0) -> str:
        """
        Initiates an observation correlation request.

        :param target_observation: A dictionary containing the observation data to correlate.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the observation correlation process.
        """
        return self.get_request_id("correlate-observation/requests", target_observation, timeout)

    def get_correlate_observation_results(
        self, request_id: str, max_retries: int = 3, retry_delay: float = 5.0, timeout: float = 20.0
    ) -> dict:
        """
        Retrieves the results of the observation correlation request.

        :param request_id: The ID of the request for which to retrieve results.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the observation correlation request.
        """
        return self.wait_for_request_result(
            f"correlate-observation/results/{request_id}/simple", max_retries, retry_delay, timeout
        )

    def determine_orbit(self, od_request: dict, timeout: float = 20.0) -> str:
        """
        Initiates an orbit determination request.

        :param od_request: A dictionary containing the target orbit data.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the orbit determination process.
        """
        return self.get_request_id("determine-orbit/wls/requests", od_request, timeout)

    def get_determine_orbit_results(
        self,
        request_id: str,
        result_format: str = "simple",
        result_part_id: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        timeout: float = 20.0,
    ) -> dict:
        """
        Retrieves the results of the orbit determination request.

        :param request_id: The ID of the request for which to retrieve results.
        :param result_part_id: Optional part ID for retrieving a specific portion of the result.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the orbit determination request.
        """
        # Validate the format parameter
        valid_formats = {"simple", "omm"}
        if result_format not in valid_formats:
            raise ValueError(
                f"Invalid format '{result_format}'. Expected one of: {', '.join(valid_formats)}."
            )

        # Construct the URL for the request
        if result_part_id is not None:
            result_url = (
                f"determine-orbit/wls/results/{request_id}/{result_format}/{result_part_id}"
            )
        else:
            result_url = f"determine-orbit/wls/results/{request_id}/{result_format}"

        # Wait for and return the request result
        return self.wait_for_request_result(result_url, max_retries, retry_delay, timeout)

    def estimate_covariance(self, target_covariance: dict, timeout: float = 20.0) -> str:
        """
        Initiates a covariance estimation request.

        :param target_covariance: A dictionary containing the target covariance data.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the covariance estimation process.
        """
        return self.get_request_id("estimate-covariance/requests", target_covariance, timeout)

    def get_estimate_covariance_results(
        self, request_id: str, max_retries: int = 3, retry_delay: float = 5.0, timeout: float = 20.0
    ) -> dict:
        """
        Retrieves the results of the covariance estimation request.

        :param request_id: The ID of the request for which to retrieve results.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the covariance estimation request.
        """
        return self.wait_for_request_result(
            f"estimate-covariance/results/{request_id}/simple", max_retries, retry_delay, timeout
        )

    def estimate_risk(self, request_body: dict, method: str, timeout: float = 20.0) -> str:
        """
        Initiates a risk estimation request based on the specified method.

        :param request_body: A dictionary containing the data for the risk estimation.
        :param method: The method of risk estimation (e.g., 'alfano-2005', 'alfriend-1999').
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the risk estimation process.
        :raises ValueError: If the specified method is invalid.
        """
        # Validate the method parameter
        valid_methods = [
            "alfano-2005",
            "alfriend-1999",
            "all-methods",
            "chan-1997",
            "foster-1992",
            "maximum-probability",
            "monte-carlo",
            "patera-2001",
            "patera-2003",
        ]
        if method not in valid_methods:
            raise ValueError(
                f"Invalid method '{method}'. Expected one of: {', '.join(valid_methods)}."
            )

        return self.get_request_id(f"estimate-risk/{method}/requests", request_body, timeout)

    def get_estimate_risk_results(
        self,
        request_id: str,
        method: str,
        result_part_id: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        timeout: float = 20.0,
    ) -> dict:
        """
        Retrieves the results of a risk estimation request based on the specified method.

        :param request_id: The ID of the request for which to retrieve results.
        :param method: The method of risk estimation used for the request.
        :param result_part_id: Optional part ID for retrieving a specific portion of the result.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the risk estimation request.
        :raises ValueError: If the specified method is invalid.
        """
        # Validate the method parameter
        valid_methods = [
            "alfano-2005",
            "alfriend-1999",
            "all-methods",
            "chan-1997",
            "foster-1992",
            "maximum-probability",
            "monte-carlo",
            "patera-2001",
            "patera-2003",
        ]
        if method not in valid_methods:
            raise ValueError(
                f"Invalid method '{method}'. Expected one of: {', '.join(valid_methods)}."
            )

        # Construct the URL for the request
        if result_part_id is not None:
            result_url = f"estimate-risk/{method}/results/{request_id}/simple/{result_part_id}"
        else:
            result_url = f"estimate-risk/{method}/results/{request_id}/simple"

        # Wait for and return the request result
        return self.wait_for_request_result(result_url, max_retries, retry_delay, timeout)

    def predict_risk(self, request_body: dict, method: str, timeout: float = 20.0) -> str:
        """
        Initiates a risk prediction request based on the specified method.

        :param request_body: A dictionary containing the data for the risk prediction.
        :param method: The method of risk prediction (e.g., 'alfano-2005', 'alfriend-1999').
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the risk prediction process.
        :raises ValueError: If the specified method is invalid.
        """
        # Validate the method parameter
        valid_methods = [
            "alfano-2005",
            "alfriend-1999",
            "all-methods",
            "chan-1997",
            "foster-1992",
            "maximum-probability",
            "monte-carlo",
            "patera-2001",
            "patera-2003",
        ]
        if method not in valid_methods:
            raise ValueError(
                f"Invalid method '{method}'. Expected one of: {', '.join(valid_methods)}."
            )

        return self.get_request_id(f"predict-risk/{method}/requests", request_body, timeout)

    def get_predict_risk_results(
        self,
        request_id: str,
        method: str,
        result_part_id: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        timeout: float = 20.0,
    ) -> dict:
        """
        Retrieves the results of a risk prediction request based on the specified method.

        :param request_id: The ID of the request for which to retrieve results.
        :param method: The method of risk prediction used for the request.
        :param result_part_id: Optional part ID for retrieving a specific portion of the result.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the risk prediction request.
        :raises ValueError: If the specified method is invalid.
        """
        # Validate the method parameter
        valid_methods = [
            "alfano-2005",
            "alfriend-1999",
            "all-methods",
            "chan-1997",
            "foster-1992",
            "maximum-probability",
            "monte-carlo",
            "patera-2001",
            "patera-2003",
        ]
        if method not in valid_methods:
            raise ValueError(
                f"Invalid method '{method}'. Expected one of: {', '.join(valid_methods)}."
            )

        # Construct the URL for the request
        if result_part_id is not None:
            result_url = f"predict-risk/{method}/results/{request_id}/simple/{result_part_id}"
        else:
            result_url = f"predict-risk/{method}/results/{request_id}/simple"

        # Wait for and return the request result
        return self.wait_for_request_result(result_url, max_retries, retry_delay, timeout)

    def propagate_orbit(self, request_body: dict, method: str, timeout: float = 20.0) -> str:
        """
        Initiates an orbit propagation request based on the specified method.

        :param request_body: A dictionary containing the data for the orbit propagation.
        :param method: The propagation method to use (e.g., 'neptune', 'sgp4').
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the orbit propagation process.
        :raises ValueError: If the specified method is invalid.
        """
        # Validate the method parameter
        valid_methods = ["neptune", "sgp4"]
        if method not in valid_methods:
            raise ValueError(
                f"Invalid method '{method}'. Expected one of: {', '.join(valid_methods)}."
            )

        return self.get_request_id(f"propagate-orbit/{method}/requests", request_body, timeout)

    def get_propagate_orbit_results(
        self,
        request_id: str,
        method: str,
        result_format: str,
        result_part_id: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        timeout: float = 20.0,
    ) -> dict:
        """
        Retrieves the results of an orbit propagation request based on the specified method.

        :param request_id: The ID of the request for which to retrieve results.
        :param method: The method of orbit propagation used for the request.
        :param result_format: The format of the results (e.g., 'oem', 'opm', 'simple').
        :param result_part_id: Optional part ID for retrieving a specific portion of the result.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the orbit propagation request.
        :raises ValueError: If the specified method or format is invalid.
        """
        # Validate the method parameter
        valid_methods = ["neptune", "sgp4"]
        if method not in valid_methods:
            raise ValueError(
                f"Invalid method '{method}'. Expected one of: {', '.join(valid_methods)}."
            )

        # Validate the format parameter
        valid_formats = ["oem", "opm", "simple"] if method == "neptune" else ["omm", "simple"]
        if result_format not in valid_formats:
            raise ValueError(
                f"Invalid format '{result_format}'. Expected one of: {', '.join(valid_formats)}."
            )

        # Construct the URL for the request
        if result_part_id is not None:
            result_url = (
                f"propagate-orbit/{method}/results/{request_id}/{result_format}/{result_part_id}"
            )
        else:
            result_url = f"propagate-orbit/{method}/results/{request_id}/{result_format}"

        # Wait for and return the request result
        return self.wait_for_request_result(result_url, max_retries, retry_delay, timeout)

    def predict_passes(self, request_body: dict, method: str, timeout: float = 20.0) -> str:
        """
        Initiates a pass prediction request based on the specified method.

        :param request_body: A dictionary containing the data for the pass prediction.
        :param method: The prediction method to use (e.g., 'neptune', 'sgp4', 'oems').
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the pass prediction process.
        :raises ValueError: If the specified method is invalid.
        """
        # Validate the method parameter
        valid_methods = ["neptune", "sgp4", "oems"]
        if method not in valid_methods:
            raise ValueError(
                f"Invalid method '{method}'. Expected one of: {', '.join(valid_methods)}."
            )

        return self.get_request_id(f"predict-passes/{method}/requests", request_body, timeout)

    def get_predict_passes_results(
        self,
        request_id: str,
        method: str,
        result_format: str,
        result_part_id: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        timeout: float = 20.0,
    ) -> dict:
        """
        Retrieves the results of a pass prediction request based on the specified method.

        :param request_id: The ID of the request for which to retrieve results.
        :param method: The method of pass prediction used for the request.
        :param result_format: The format of the results (e.g., 'simple', 'summary').
        :param result_part_id: Optional part ID for retrieving a specific portion of the result.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the pass prediction request.
        :raises ValueError: If the specified method or format is invalid.
        """
        # Validate the method parameter
        valid_methods = ["neptune", "sgp4", "oems"]
        if method not in valid_methods:
            raise ValueError(
                f"Invalid method '{method}'. Expected one of: {', '.join(valid_methods)}."
            )

        # Validate the format parameter
        valid_formats = ["simple", "summary"]
        if result_format not in valid_formats:
            raise ValueError(
                f"Invalid format '{result_format}'. Expected one of: {', '.join(valid_formats)}."
            )

        # Construct the URL for the request
        if result_part_id is not None:
            result_url = (
                f"predict-passes/{method}/results/{request_id}/{result_format}/{result_part_id}"
            )
        else:
            result_url = f"predict-passes/{method}/results/{request_id}/{result_format}"

        # Wait for and return the request result
        return self.wait_for_request_result(result_url, max_retries, retry_delay, timeout)

    def check_orbit(self, request_body: dict, timeout: float = 20.0) -> str:
        """
        Initiates an orbit check request.

        :param request_body: A dictionary containing the required data for checking orbit.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the orbit check process.
        """
        return self.get_request_id("check-orbit/requests", request_body, timeout)

    def get_check_orbit_results(
        self, request_id: str, max_retries: int = 3, retry_delay: float = 5.0, timeout: float = 20.0
    ) -> dict:
        """
        Retrieves the results of the orbit check request.

        :param request_id: The ID of the request for which to retrieve results.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the orbit check request.
        """
        return self.wait_for_request_result(
            f"check-orbit/results/{request_id}/simple", max_retries, retry_delay, timeout
        )

    def generate_maneuver(self, request_body: dict, timeout: float = 20.0) -> str:
        """
        Initiates a maneuver generation request.

        :param request_body: A dictionary containing the required data for generating a maneuver.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the maneuver generation process.
        """
        return self.get_request_id("generate-maneuver/requests", request_body, timeout)

    def get_generate_maneuver_results(
        self,
        request_id: str,
        result_part_id: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        timeout: float = 20.0,
    ) -> dict:
        """
        Retrieves the results of the maneuver generation request.

        :param request_id: The ID of the request for which to retrieve results.
        :param result_part_id: Optional part ID for retrieving a specific portion of the result.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the maneuver generation request.
        """
        # Construct the URL for the request
        if result_part_id is not None:
            result_url = f"generate-maneuver/results/{request_id}/simple/{result_part_id}"
        else:
            result_url = f"generate-maneuver/results/{request_id}/simple"

        # Wait for and return the request result
        return self.wait_for_request_result(result_url, max_retries, retry_delay, timeout)

    def maneuver_execution_analysis(self, request_body: dict, timeout: float = 20.0) -> str:
        """
        Initiates a maneuver execution analysis request.

        :param request_body: A dictionary containing the required data for maneuver analysis.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the maneuver execution analysis process.
        """
        return self.get_request_id("maneuver-execution-analysis/requests", request_body, timeout)

    def get_maneuver_execution_analysis_results(
        self, request_id: str, max_retries: int = 3, retry_delay: float = 5.0, timeout: float = 20.0
    ) -> dict:
        """
        Retrieves the results of the maneuver execution analysis request.

        :param request_id: The ID of the request for which to retrieve results.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the maneuver execution analysis request.
        """
        return self.wait_for_request_result(
            f"maneuver-execution-analysis/results/{request_id}/simple",
            max_retries,
            retry_delay,
            timeout,
        )
