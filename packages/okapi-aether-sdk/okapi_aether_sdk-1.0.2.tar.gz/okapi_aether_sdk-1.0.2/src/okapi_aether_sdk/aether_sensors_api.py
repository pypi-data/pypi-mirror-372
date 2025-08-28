from typing import Any, List, Optional, Union

from okapi_aether_sdk.aether_api import AetherApi


class AetherSensorsApi(AetherApi):
    """
    AetherSensorsApi class that provides methods for interacting
    with sensor-related endpoints of the Aether API.

    This class inherits from AetherApi and utilizes its methods
    for sending requests and handling responses related to sensor systems.
    """

    def get_sensor_systems(self, limit: int = 20, timeout: float = 20.0) -> Optional[List[Any]]:
        """
        Retrieves a list of sensor systems.

        :param limit: Maximum results per page (default 20); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of sensor systems.
        """
        if limit is None:
            return self.get_all_elements("sensor-systems", timeout)

        return self.get_elements(f"sensor-systems?limit={limit}", timeout)

    def get_sensor_system(self, sensor_system_id: str, timeout: float = 20.0) -> dict:
        """
        Retrieves a specific sensor system by its ID.

        :param sensor_system_id: The ID of the sensor system to retrieve.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The sensor system information as a dictionary.
        """
        return self.get(f"sensor-systems/{sensor_system_id}", timeout=timeout)

    def add_sensor_system(self, sensor_system_to_add: dict, timeout: float = 20.0) -> dict:
        """
        Adds a new sensor system.

        :param sensor_system_to_add: A dictionary containing the sensor system data.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the sensor system addition process.
        """
        return self.post("sensor-systems", sensor_system_to_add, timeout)

    def get_tdms(
        self,
        filters: Optional[dict] = None,
        page: int = 1,
        limit: Optional[int] = 20,
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves a list of TDMS (Tracking Data Message) based on filters.

        :param filters: Optional dictionary of filters to apply, with the following fields:
            {
                "insert_epoch": dict,
                "epoch": dict,
                "cospar_id" str,
                "norad_id": int
            }
            Where each dictionary value can take the following form:
                {
                    "$lt": str (ISO timestamp),
                    "$lte": str (ISO timestamp),
                    "$gt": str (ISO timestamp),
                    "$gte": str (ISO timestamp),
                    "$eq": str (ISO timestamp)
                }
        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 20); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of TDMS records.
        """
        filters = filters or {}
        query = self._build_query(filters)

        if limit is None:
            sep = "?" if query else ""
            return self.get_all_elements(f"tdms{sep}{query}", timeout)

        sep = "&" if query else ""
        return self.get_elements(f"tdms?{query}{sep}page={page}&limit={limit}", timeout)

    def get_tdm(self, tdm_id: str, timeout: float = 20.0) -> dict:
        """
        Retrieves a specific TDM by its ID.

        :param tdm_id: The ID of the TDM to retrieve.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The TDM information as a dictionary.
        """
        return self.get(f"tdms/{tdm_id}", timeout=timeout)

    def add_tdms(
        self, tdm_data: Union[dict, List[dict]], timeout: float = 20.0
    ) -> Union[dict, List[dict]]:
        """
        Initiates the addition of one or more TDMS.

        :param tdm_data: A dictionary or a list of dictionaries containing the TDM data to add.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A dictionary with the added TDM ID for a single TDM,
                or a list of added TDMS if multiple are provided.
        """
        # Ensure that tdm_data is a list
        if not isinstance(tdm_data, list):
            tdm_data = [tdm_data]  # Wrap in a list if it's a single TDM

        added_tdms = []
        for tdm in tdm_data:
            added_tdm = self.post("tdms", tdm, timeout)
            added_tdms.append(added_tdm)

        # Return a single added TDM if only one was provided
        return added_tdms[0] if len(added_tdms) == 1 else added_tdms

    def get_ground_station_passes(
        self,
        filters: Optional[dict] = None,
        page: int = 1,
        limit: Optional[int] = 20,
        timeout: float = 20.0,
    ) -> Optional[List[Any]]:
        """
        Retrieves ground station passes based on filters.

        :param filters: Optional dictionary of filters to apply, with the following fields:
            {
                "start": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                "stop": str (ISO timestamp, e.g., '2025-01-01T09:30Z'),
                "objectId" str,
                "name": str,
            }
        :param page: The page number for pagination.
        :param limit: Maximum results per page (default 20); use None for all results.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: A list of ground station passes.
        """
        filters = filters or {}
        query = self._build_query(filters)

        if limit is None:
            sep = "?" if query else ""
            return self.get_all_elements(f"multi-ground-station-passes-info{sep}{query}", timeout)

        sep = "&" if query else ""
        return self.get_elements(
            f"multi-ground-station-passes-info?{query}{sep}page={page}&limit={limit}", timeout
        )

    def add_ground_station_pass(self, pass_to_add: dict, timeout: float = 20.0) -> dict:
        """
        Initiates the addition of a new ground station pass.

        :param pass_to_add: A dictionary containing the ground station pass data.
        :param timeout: Maximum time to wait for a response, in seconds.
        :return: The request ID for the ground station pass addition process.
        """
        return self.post("multi-ground-station-passes", pass_to_add, timeout)
