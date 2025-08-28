import json
from typing import Any, List, Literal, Optional

from okapi_aether_sdk.aether_api import AetherApi


class AetherSatellitesApi(AetherApi):
    """
    AetherSatellitesApi class that provides methods for interacting
    with satellite-related endpoints of the Aether API.

    This class inherits from AetherApi and utilizes its methods
    for sending requests and handling responses.
    """

    def get_satellites(
        self, page: int = 1, limit: Optional[int] = 20, timeout: float = 20.0
    ) -> Optional[List[Any]]:
        """
        Retrieves a list of satellites.

        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 20); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of satellites.
        """
        if limit is None:
            return self.get_all_elements("satellites", timeout)

        return self.get_elements(f"satellites?page={page}&limit={limit}", timeout)

    def get_satellite(self, satellite_id: str, timeout: float = 20.0) -> dict:
        """
        Retrieves a specific satellite by its ID.

        :param satellite_id: The ID of the satellite to retrieve.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The satellite information as a dictionary.
        """
        return self.get(f"satellites/{satellite_id}", timeout=timeout)

    def add_satellite(self, satellite_to_add: dict, timeout: float = 20.0) -> dict:
        """
        Adds a new satellite.

        :param satellite_to_add: A dictionary containing the satellite data.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The added satellite data including the satellite ID.
        """
        return self.post("satellites", satellite_to_add, timeout)

    def change_satellite(self, satellite_to_change: dict, timeout: float = 20.0) -> dict:
        """
        Changes the properties of an existing satellite.

        :param satellite_to_change: A dictionary containing the updated satellite data.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The changed satellite data including the satellite ID.
        """
        if "satellite_id" not in satellite_to_change:
            raise ValueError("satellite_to_change must contain a 'satellite_id' key")

        return self.put(
            f"satellites/{satellite_to_change['satellite_id']}", satellite_to_change, timeout
        )

    def update_satellite(self, satellite_to_update: dict, timeout: float = 20.0) -> dict:
        """
        Updates an existing satellite's information.

        :param satellite_to_update: A dictionary containing the satellite's updated data.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The updated satellite data including the satellite ID.
        """
        if "satellite_id" not in satellite_to_update:
            raise ValueError("satellite_to_update must contain a 'satellite_id' key")

        return self.patch(
            f"satellites/{satellite_to_update['satellite_id']}", satellite_to_update, timeout
        )

    def delete_satellite(self, satellite_id: str, timeout: float = 20.0) -> dict:
        """
        Deletes a satellite by its ID.

        :param satellite_id: The ID of the satellite to delete.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The deleted satellite data including the satellite ID.
        """
        return self.delete(f"satellites/{satellite_id}", timeout)

    def get_satellite_oems(
        self,
        satellite_id: str,
        result_format: Literal["json", "kvn", "xml"] = "json",
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves OEMs (Orbit Ephemeris Messages) associated with a specific satellite.

        :param satellite_id: The ID of the satellite.
        :param result_format: Output format of the data. Must be one of "json", "kvn", or "xml".
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of OEMs associated with the satellite.
        """
        if result_format == "json":
            return self.get_elements(f"satellites/{satellite_id}/oems", timeout)
        return self.get_elements(f"satellites/{satellite_id}/oems?format={result_format}", timeout)

    def get_satellite_neighborhoods(
        self, satellite_id: str, filters: Optional[dict] = None, timeout: float = 20.0
    ) -> Optional[List[Any]]:
        """
        Retrieves neighborhoods around a specific satellite.

        :param satellite_id: The ID of the satellite.
        :param filters: Optional dictionary of filters to apply, with the following fields:
            {
                "tca": str (ISO timestamp, e.g., '2025-01-01T09:30Z') | dict,
                "miss_distance": float | dict,
                "miss_distance_r": float | dict,
                "miss_distance_t": float | dict,
                "miss_distance_n": float | dict
            }
            Where each dictionary value can take the following form:
                {
                    "$lt": float | str (ISO timestamp) for 'tca',
                    "$lte": float | str (ISO timestamp) for 'tca',
                    "$gt": float | str (ISO timestamp) for 'tca',
                    "$gte": float | str (ISO timestamp) for 'tca',
                    "$eq": float | str (ISO timestamp) for 'tca'
                }
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of neighborhoods surrounding the satellite.
        """
        filters = filters or {}

        query = self._build_query(filters)
        sep = "?" if query else ""
        return self.get_elements(f"satellites/{satellite_id}/neighborhoods{sep}{query}", timeout)

    def get_oems(
        self,
        filters: Optional[dict] = None,
        result_format: Literal["json", "kvn", "xml"] = "json",
        page: int = 1,
        limit: Optional[int] = 20,
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves a list of OEMs from the API.

        :param filters: Optional dictionary of filters to apply, with the following fields:
            {
                "fov": {
                    "sensor_id": str,
                    "start_epoch": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                    "stop_epoch": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                    "radius": float,
                    "angle_1": float,
                    "angle_2": float,
                    "angle_type": str ("AZEL" | "RADEC")
                },
                "epoch": dict,
                "tracklet_id": str (UUID),
                "is_predicted": bool,
                "norad_id": str,
                "orbit_type": str ("GEO" | "geo" | "IGO" | "igo" | "EGO" | "ego" | "NSO" | "nso" |
                                   "GTO" | "gto" | "MEO" | "meo" | "GHO" | "gho" | "LEO" | "leo" |
                                   "HAO" | "hao" | "MGO" | "mgo" | "HEO" | "heo"),
                "inclination": dict,
                "period": dict,
                "eccentricity": dict,
                "periapsis": dict,
                "apoapsis": dict
            }
            Where each dictionary value can take the following form:
                {
                    "$lt": float | str (ISO timestamp) for 'epoch',
                    "$lte": float | str (ISO timestamp) for 'epoch',
                    "$gt": float | str (ISO timestamp) for 'epoch',
                    "$gte": float | str (ISO timestamp) for 'epoch',
                    "$eq": float | str (ISO timestamp) for 'epoch'
                }
        :param result_format: Output format of the data. Must be one of "json", "kvn", or "xml".
        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 20); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of OEMs.
        """
        filters = filters or {}
        query = self._build_query(filters)
        sep = "&" if query else ""

        if limit is None:
            return self.get_all_elements(f"oems?{query}{sep}format={result_format}", timeout)

        if result_format == "json":
            return self.get_elements(f"oems?{query}{sep}page={page}&limit={limit}", timeout)

        return self.get_elements(
            f"oems?{query}{sep}format={result_format}&page={page}&limit={limit}", timeout
        )

    def get_oem(
        self,
        oem_id: str,
        result_format: Literal["json", "kvn", "xml"] = "json",
        timeout: float = 20.0,
    ) -> dict:
        """
        Retrieves a specific OEM by its ID.

        :param oem_id: The ID of the OEM to retrieve.
        :param result_format: Output format of the data. Must be one of "json", "kvn", or "xml".
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The OEM information as a dictionary.
        """
        if result_format == "json":
            return self.get(f"oems/{oem_id}", timeout=timeout)
        return self.get(f"oems/{oem_id}?format={result_format}", timeout=timeout)

    def get_od_residuals_plot(self, oem_id: str, timeout: float = 20.0) -> str:
        """
        Retrieve the OD residuals plot (HTML) for a given OEM ID.

        :param oem_id: The ID of the OEM to fetch the plot for.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A string containing the parsed HTML content from the response.
        """
        return self.get(f"oems/{oem_id}/plot-od-residuals", "html", timeout)

    def get_omms(
        self,
        filters: Optional[dict] = None,
        result_format: Literal["json", "kvn", "xml"] = "json",
        page: int = 1,
        limit: Optional[int] = 100,
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves a list of OMMs (Orbit Maintenance Messages).

        :param filters: Optional dictionary of filters to apply, with the following fields:
            {
                "fov": {
                    "sensor_id": str,
                    "start_epoch": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                    "stop_epoch": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                    "radius": float,
                    "angle_1": float,
                    "angle_2": float,
                    "angle_type": str ("AZEL" | "RADEC")
                },
                "originator": str ("18 SPCS" | "EON" | "OKAPI:ORBITS" | "18 spcs" | "eon" | "OKAPI:Orbits"),
                "latest": bool,
                "start": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                "stop": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                "norad_id": int,
                "cospar_id": str,
                "orbit_type": str ("GEO" | "geo" | "IGO" | "igo" | "EGO" | "ego" | "NSO" | "nso" |
                                   "GTO" | "gto" | "MEO" | "meo" | "GHO" | "gho" | "LEO" | "leo" |
                                   "HAO" | "hao" | "MGO" | "mgo" | "HEO" | "heo"),
                "inclination": dict,
                "period": dict,
                "eccentricity": dict,
                "periapsis": dict,
                "apoapsis": dict,
                "semimajoraxis": dict
            }
            Where each dictionary value can take the following form:
                {
                    "$lt": float,
                    "$lte": float,
                    "$gt": float,
                    "$gte": float,
                    "$eq": float
                }
        :param result_format: Output format of the data. Must be one of "json", "kvn", or "xml".
        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 100); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of OMMs.
        """
        filters = filters or {}
        query = self._build_query(filters)
        sep = "&" if query else ""

        if limit is None:
            return self.get_all_elements(f"omms?{query}{sep}format={result_format}", timeout)

        if result_format == "json":
            return self.get_elements(f"omms?{query}{sep}page={page}&limit={limit}", timeout)

        return self.get_elements(
            f"omms?{query}{sep}format={result_format}&page={page}&limit={limit}", timeout
        )

    def get_tles(
        self,
        filters: Optional[dict] = None,
        page: int = 1,
        limit: Optional[int] = 1000,
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves a list of TLEs (Two-Line Element sets).

        :param filters: Optional dictionary of filters to apply, with the following fields:
            {
                "originator": str ("18 SPCS" | "EON" | "OKAPI:ORBITS" | "18 spcs" | "eon" | "OKAPI:Orbits"),
                "format": str ("JSON" | "BATCH" | "json" | "batch"),
                "latest": bool,
                "start": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                "stop": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                "norad_id": int,
                "cospar_id": str,
                "orbit_type": str ("GEO" | "geo" | "IGO" | "igo" | "EGO" | "ego" | "NSO" | "nso" |
                                   "GTO" | "gto" | "MEO" | "meo" | "GHO" | "gho" | "LEO" | "leo" |
                                   "HAO" | "hao" | "MGO" | "mgo" | "HEO" | "heo"),
                "inclination": dict,
                "period": dict,
                "eccentricity": dict,
                "periapsis": dict,
                "apoapsis": dict,
                "semimajoraxis": dict
            }
            Where each dictionary value can take the following form:
                {
                    "$lt": float,
                    "$lte": float,
                    "$gt": float,
                    "$gte": float,
                    "$eq": float
                }
        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 1000); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of TLEs.
        """
        filters = filters or {}
        query = self._build_query(filters)

        if limit is None:
            sep = "?" if query else ""
            return self.get_all_elements(f"tles{sep}{query}", timeout)

        sep = "&" if query else ""
        return self.get_elements(f"tles?{query}{sep}page={page}&limit={limit}", timeout)

    def get_cdms(
        self,
        filters: Optional[dict] = None,
        result_format: Literal["json", "kvn", "xml"] = "json",
        page: int = 1,
        limit: Optional[int] = 20,
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves a list of CDMs (Conjunction Data Messages).

        :param filters: Optional dictionary of filters to apply, with the following fields:
            {
                "sort": str,
                "sat1_object_designator": int,
                "sat2_object_designator": int,
                "inserted": dict,
                "relative_position_r": dict,
                "relative_position_t": dict,
                "relative_position_n": dict,
                "time_to_tca": dict,
                "exclude": list[str],
                "include": list[str]
            }
            Where each dictionary value can take the following form:
                {
                    "$lt": float | str (ISO timestamp) for 'inserted' | int for 'time_to_tca',
                    "$lte": float | str (ISO timestamp) for 'inserted' | int for 'time_to_tca',
                    "$gt": float | str (ISO timestamp) for 'inserted' | int for 'time_to_tca',
                    "$gte": float | str (ISO timestamp) for 'inserted' | int for 'time_to_tca',
                    "$eq": float | str (ISO timestamp) for 'inserted' | int for 'time_to_tca'
                }
        :param result_format: Output format of the data. Must be one of "json", "kvn", or "xml".
        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 20); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of CDMs.
        """
        filters = filters or {}
        query = self._build_query(filters)
        sep = "&" if query else ""

        if limit is None:
            return self.get_all_elements(f"cdms?{query}{sep}format={result_format}", timeout)

        if result_format == "json":
            return self.get_elements(f"cdms?{query}{sep}page={page}&limit={limit}", timeout)

        return self.get_elements(
            f"cdms?{query}{sep}format={result_format}&page={page}&limit={limit}", timeout
        )

    def upload_cdm(self, cdm_to_upload: dict, timeout: float = 20.0) -> str:
        """
        Initiates the upload of a Conjunction Data Message.

        :param cdm_to_upload: A dictionary containing the CDM data to upload.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the CDM upload process.
        """
        return self.get_request_id("cdms/requests", cdm_to_upload, timeout)

    def get_upload_cdm_results(
        self, request_id: str, max_retries: int = 3, retry_delay: float = 5.0, timeout: float = 20.0
    ) -> dict:
        """
        Waits for the results of a CDM upload based on the request ID.

        :param request_id: The ID of the upload request.
        :param max_retries: Maximum number of retry attempts.
        :param retry_delay: Time (in seconds) to wait between retries.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The results of the CDM upload process.
        """
        return self.wait_for_request_result(
            f"cdms/results/{request_id}/simple", max_retries, retry_delay, timeout
        )

    def get_conjunctions(
        self,
        filters: Optional[dict] = None,
        page: int = 1,
        limit: Optional[int] = 100,
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves a list of conjunctions.

        :param filters: Optional dictionary of filters to apply, with the following fields:
            {
                "sort": str,
                "tca": dict,
                "collision_probability": float | dict,
                "miss_distance": float | dict,
                "criticality": list[str] ("non_critical" | "observe" | "critical"),
                "q": str,
                "include": list[str]
                "exclude": list[str] ("newest_risk_estimation" | "newest_risk_prediction"),
            }
            Where each dictionary value can take the following form:
                {
                    "$lte": float | str (ISO timestamp) for 'tca',
                    "$gte": float | str (ISO timestamp) for 'tca'
                }
        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 100); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of conjunctions.
        """
        filters = filters or {}
        query = self._build_query(filters)

        if limit is None:
            sep = "?" if query else ""
            return self.get_all_elements(f"conjunctions{sep}{query}", timeout)

        sep = "&" if query else ""
        return self.get_elements(f"conjunctions?{query}{sep}page={page}&limit={limit}", timeout)

    def get_conjunction(self, conjunction_id: str, timeout: float = 20.0) -> dict:
        """
        Retrieves a specific conjunction by its ID.

        :param conjunction_id: The ID of the conjunction to retrieve.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The conjunction information as a dictionary.
        """
        return self.get(f"conjunctions/{conjunction_id}", timeout=timeout)

    def get_conjunction_risk_estimations(
        self, conjunction_id: str, timeout: float = 20.0
    ) -> Optional[List[Any]]:
        """
        Retrieves risk estimations for a specific conjunction.

        :param conjunction_id: The ID of the conjunction.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of risk estimations associated with the conjunction.
        """
        return self.get_elements(f"conjunctions/{conjunction_id}/risk-estimations", timeout)

    def get_conjunction_risk_predictions(
        self, conjunction_id: str, timeout: float = 20.0
    ) -> Optional[List[Any]]:
        """
        Retrieves risk predictions for a specific conjunction.

        :param conjunction_id: The ID of the conjunction.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of risk predictions associated with the conjunction.
        """
        return self.get_elements(f"conjunctions/{conjunction_id}/risk-predictions", timeout)

    def get_conjunction_cdms(
        self,
        conjunction_id: str,
        result_format: Literal["json", "kvn", "xml"] = "json",
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves CDMs associated with a specific conjunction.

        :param conjunction_id: The ID of the conjunction.
        :param result_format: Output format of the data. Must be one of "json", "kvn", or "xml".
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of CDMs associated with the conjunction.
        """
        if result_format == "json":
            return self.get_elements(f"conjunctions/{conjunction_id}/cdms", timeout)
        return self.get_elements(
            f"conjunctions/{conjunction_id}/cdms?format={result_format}", timeout
        )

    def get_conjunction_maneuver_evaluations(
        self, conjunction_id: str, timeout: float = 20.0
    ) -> Optional[List[Any]]:
        """
        Retrieves maneuver evaluations for a specific conjunction.

        :param conjunction_id: The ID of the conjunction.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of maneuver evaluations associated with the conjunction.
        """
        return self.get_elements(f"conjunctions/{conjunction_id}/maneuver-evals", timeout)

    def get_maneuver_plans(
        self, page: int = 1, limit: Optional[int] = 20, timeout: float = 20.0
    ) -> Optional[List[Any]]:
        """
        Retrieves a list of maneuver plans.

        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 20); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of maneuver plans.
        """
        if limit is None:
            return self.get_all_elements("maneuver-plans", timeout)

        return self.get_elements(f"maneuver-plans?page={page}&limit={limit}", timeout)

    def add_maneuver_plan(
        self, maneuver_plan_to_add: dict, force: Optional[bool] = False, timeout: float = 20.0
    ) -> dict:
        """
        Adds a new maneuver plan.

        :param maneuver_plan_to_add: A dictionary containing the maneuver plan data.
        :param force: Optional parameter to force the addition if necessary.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the maneuver plan addition process.
        """
        return self.post(f"maneuver-plans?force={json.dumps(force)}", maneuver_plan_to_add, timeout)

    def calculate_uncertainties(
        self,
        filters: Optional[dict] = None,
        page: int = 1,
        limit: Optional[int] = 1000,
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves uncertainty values based on specified filters.

        :param filters: Optional dictionary of filters to apply, with the following fields:
            {
                "epoch": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                "norad_id": list[int],
                "cospar_id": list[str],
                "sort": list[str] ("sum" | "-sum" | "rtn.r" | "-rtn.r" | "rtn.t" | "-rtn.t" | "rtn.n" "-rtn.n")
            }
        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 1000); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of uncertainty values.
        """
        filters = filters or {}
        query = self._build_query(filters)

        if limit is None:
            sep = "?" if query else ""
            return self.get_all_elements(f"uncertainties{sep}{query}", timeout)

        sep = "&" if query else ""
        return self.get_elements(f"uncertainties?{query}{sep}page={page}&limit={limit}", timeout)
