import arrow
import json
import requests

from typing import Dict, Optional, List
from services.dataclasses import Movement


class VoultService:
    URL_MAP = {
        "qa": "https://gpiwebcbvectorwinqa.azurewebsites.net/",
        "prod": "https://portalclientes.vectorcapital.cl/",
    }

    BASE_HEADERS = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    def __init__(self, username: str, password: str, environment: str = "qa", results_as_objects: bool = False) -> None:
        self.url = self.URL_MAP.get(environment) or self.URL_MAP["qa"]
        self.username = username
        self._password = password
        self._token = self.__get_auth_token()
        self._results_as_objects = results_as_objects

        self._auth_headers = {
            "Authorization": f"Bearer {self._token}",
            **self.BASE_HEADERS,
        }

    def __get_auth_token(self) -> str:
        url = f"{self.url}api/publicapi/shared/Auth/SignIn"
        data = {
            "userName": self.username,
            "password": self._password
        }

        response = requests.post(url, headers=self.BASE_HEADERS, data=json.dumps(data))
        response_json = response.json()
        return response_json['token']

    def refresh_token(self) -> None:
        token = self.__get_auth_token()
        setattr(self, "_token", token)
        setattr(self, "_auth_headers", {
            "Authorization": f"Bearer {self._token}",
            **self.BASE_HEADERS,
        })
        print("token has been refreshed")

    def get_voult_info(self, document_number: str) -> Optional[Dict]:
        url = f"{self.url}api/publicapi/creasys/Clientes"
        params = {
            "Identificador": document_number,
            "CodEstado": "",
            "PageNumber": 1,
            "PageSize": 100
        }

        response = requests.get(url, headers=self._auth_headers, params=params)
        if response.status_code != 200:
            print(f"Error getting voult info for document number {document_number}: {response.text}")
            return None
        return response.json()

    def get_voult_operations(self, document_number: str, from_date: str, to_date: str, page_number: int = 1) -> Optional[List[Dict]]:
        url = f"{self.url}api/publicapi/creasys/Operaciones"
        params = {
            "Identificador": document_number,
            "Desde": from_date,
            "Hasta": to_date,
            "PageNumber": page_number,
            "PageSize": 100
        }

        try:
            response = requests.get(url, headers=self._auth_headers, params=params)
            if response.status_code != 200:
                if page_number == 1:
                    print(f"Error getting voult operations for document number {document_number}: {response.text}")
                return None
            return response.json()
        except Exception as e:
            if page_number == 1:
                print(f"Error getting voult operations for document number {document_number}: {e}")
            return None

    def get_voult_movements(self, document_number: str, from_date: str, to_date: str, page_number: int = 1) -> Optional[List[Dict]]:
        url = f"{self.url}api/publicapi/creasys/Movimientos"
        params = {
            "Identificador": document_number,
            "Desde": from_date,
            "Hasta": to_date,
            "PageNumber": page_number,
            "PageSize": 100
        }

        try:
            response = requests.get(url, headers=self._auth_headers, params=params)
            if response.status_code != 200:
                if page_number == 1:
                    print(f"Error getting voult movements for document number {document_number}: {response.text}")
                return None
            result = response.json()
            if self._results_as_objects:
                return [
                    Movement(
                        id=movement["id"],
                        code_movement_type=movement["codTipoMovimiento"],
                        account_number=movement["numCuenta"],
                        movement_type=movement["tipoMovimiento"],
                        description=movement["dscMovimiento"],
                        movement_date=arrow.get(movement["fechaMovimiento"]),
                        settlement_date=arrow.get(movement["fechaLiquidacion"]),
                        amount=movement["monto"],
                        currency_code=movement["codMoneda"],
                        account_description=movement["dscCajaCuenta"],
                        movement_status=movement["dscEstadoMovimiento"],
                    )
                    for movement in result
                ]
        except Exception as e:
            if page_number == 1:
                print(f"Error getting voult movements for document number {document_number}: {e}")
            return None
