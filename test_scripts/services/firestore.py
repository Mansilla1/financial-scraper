import json
import uuid

from firebase_admin import credentials, firestore, initialize_app
from numbers import Number
from typing import Any, List, Dict, Union, Optional

from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud import firestore as gc_firestore, pubsub_v1
from google.cloud.firestore_v1.base_document import DocumentSnapshot

from .dataclasses import SpotOperationData, DocumentInformationData
from .utils import chunks


CERTIFICATE = "../serviceKeyProd.json"
CERTIFICATE_QA = "../serviceKeyDev.json"


class FirestoreConnectionService:
    RACIONAL_ENV_APP_MAP = {
        "qa": "racional-app-dev-qa",
        "prod": "racional-prod",
    }

    def __init__(self, environment: str = "qa"):
        certificate_env_dict = {
            "qa": CERTIFICATE_QA,
            "prod": CERTIFICATE,
        }
        print(f"Connecting to firestore {environment}...")
        certificate = certificate_env_dict.get(environment) or certificate_env_dict["qa"]
        cred = credentials.Certificate(certificate)
        self._app = initialize_app(cred, name=f"{environment}-app")

        self.racional_app_name = self.RACIONAL_ENV_APP_MAP.get(environment) or self.RACIONAL_ENV_APP_MAP["qa"]
        self.firestore_connection = self.get_connection()

    def get_connection(self) -> firestore.Client:
        return firestore.client(self._app)

    def get_dw_assets(self) -> gc_firestore.DocumentSnapshot:
        print("Getting drivewealth assets...")
        db = self.firestore_connection

        return db.collection("assets").where(
            "drivewealthAsset", "==", True
        ).get()

    def get_assets(self) -> gc_firestore.DocumentSnapshot:
        print("Getting assets...")
        db = self.firestore_connection

        return db.collection("assets").get()

    def get_asset_period_info_by_asset_id(self, asset_id: str) -> gc_firestore.DocumentSnapshot:
        print(f"Getting asset info (assetId: {asset_id})...")
        db = self.firestore_connection
        return db.collection("assets").document(asset_id).collection("assetInfo").document("periodsInfo").get()

    def get_document_data_and_information(self, document_name: str) -> DocumentInformationData:
        print(f"Getting document data and information (document: {document_name})...")
        db = self.firestore_connection
        document = db.document(document_name).get()
        if not document.exists:
            return DocumentInformationData(data={}, sub_documents=[])

        document_data = document.to_dict()
        sub_documents = [ref.id for ref in document.reference.collections()]
        return DocumentInformationData(data=document_data, sub_documents=sub_documents)

    def get_document_collections(self, document: str) -> None:
        print(f"Getting document collections (document: {document})...")
        db = self.firestore_connection
        return db.document(document).collections()

    def get_document_ref_data(self, document_ref: DocumentSnapshot) -> Dict:
        print(f"Getting document ref data (document: {document_ref})...")
        return document_ref.to_dict()

    def get_users_portfolio_by_chunks(self, users_ids: List[str], chunk_size: int = 20) -> List[Dict[str, Any]]:
        print("Getting users portfolio...")
        db = self.firestore_connection
        chunks_ = chunks(lst=users_ids, chunk_size=chunk_size)
        result = []
        for chunk in chunks_:
            users_portfolio = db.collection("portfolios").where(
                filter=FieldFilter("userId", "in", chunk),
            ).get()
            result.extend(list(map(lambda x:{**x.to_dict(), "id": x.id}, users_portfolio)))

        return result

    def get_users_orders_by_chunks(self, users_ids: List[str], chunk_size: int = 20) -> List[Dict[str, Any]]:
        print("Getting users orders...")
        db = self.firestore_connection
        chunks_ = chunks(lst=users_ids, chunk_size=chunk_size)
        result = []
        for chunk in chunks_:
            users_orders = db.collection("orders").where(
                filter=FieldFilter("userId", "in", chunk),
            ).get()
            result.extend(list(map(lambda x: x.to_dict(), users_orders)))

        return result

    def get_bulk_orders_by_ids(self, orders_ids: List[str], chunk_size: int = 30) -> List[Dict[str, Any]]:
        print("Getting orders...")
        db = self.firestore_connection
        chunks_ = chunks(lst=orders_ids, chunk_size=chunk_size)
        result = []
        for chunk in chunks_:
            orders = db.collection("orders").where(
                filter=FieldFilter("id", "in", chunk),
            ).get()
            result.extend(list(map(lambda x: x.to_dict(), orders)))

        return result

    def get_bulk_withdrawals(self, withdrawals_ids: List[str], chunk_size: int = 20) -> List[Dict[str, Any]]:
        print("Getting withdrawals...")
        db = self.firestore_connection
        chunks_ = chunks(lst=withdrawals_ids, chunk_size=chunk_size)
        result = []
        for chunk in chunks_:
            withdrawals = db.collection("withdrawals").where(
                filter=FieldFilter("id", "in", chunk),
            ).get()
            result.extend(list(map(lambda x: x.to_dict(), withdrawals)))

        return result

    def get_bulk_deposits(self, deposits_ids: List[str], chunk_size: int = 20) -> List[Dict[str, Any]]:
        print("Getting deposits...")
        db = self.firestore_connection
        chunks_ = chunks(lst=deposits_ids, chunk_size=chunk_size)
        result = []
        for chunk in chunks_:
            deposits = db.collection("deposits").where(
                filter=FieldFilter("id", "in", chunk),
            ).get()
            result.extend(list(map(lambda x: x.to_dict(), deposits)))

        return result

    def sub_document_data_documents(self, document_path: str) -> List[str]:
        print(f"Getting sub document data documents (document: {document_path})...")
        db = self.firestore_connection
        document = db.collection(document_path).get()
        if not document:
            return []

        return [ref.id for ref in document]

    def update_document_from_dict(self, document_destination: str, data: Dict) -> None:
        print(f"Updating document from dict (document: {document_destination})...")
        db = self.firestore_connection
        doc_ref = db.document(document_destination)
        doc_ref.set(data)

    def get_assets_periods_info_by_assets_ids(
        self,
        assets_ids: List[str],
    ) -> Dict[str, List[Dict[str, str]]]:
        print(f"Getting assets periods info (assets: {' '.join(assets_ids)})...")

        db = self.firestore_connection
        result = {}

        for asset_id in assets_ids:
            doc_snapshot = db.collection("assets").document(asset_id).collection('assetInfo').document('periodsInfo').get()
            asset_periods_info = (doc_snapshot.to_dict() or {}).get("assetPeriodsInfo", [])
            if not asset_periods_info:
                continue

            result[asset_id] = asset_periods_info

        return result

    def update_assets_periods_info_by_assets_ids(
        self,
        data_to_update: Dict[str, List[str]],
    ) -> Dict[str, List[Dict[str, str]]]:
        print(f"Updating assets periods info (assets: {' '.join(list(data_to_update.keys()))})...")

        db = self.firestore_connection

        for asset_id, data_to_update in data_to_update.items():
            doc_snapshot = db.collection("assets").document(asset_id).collection('assetInfo').document('periodsInfo')
            doc_snapshot.set({"assetPeriodsInfo": data_to_update})

        print("Update complete.")

    def get_assets_historical_prices_dict_by_assets_ids(
        self,
        assets_ids: List[str],
    ) -> Dict[str, List[Dict[str, str]]]:
        print(f"Getting assets historical prices (assets: {' '.join(assets_ids)})...")

        db = self.firestore_connection
        result = {}

        for asset_id in assets_ids:
            doc_snapshot = db.collection("assetsHistoricalPrices").document(asset_id).get()
            asset_historical_prices = (doc_snapshot.to_dict() or {}).get("values", [])
            if not asset_historical_prices:
                continue

            result[asset_id] = asset_historical_prices

        return result

    def update_assets_historical_prices(
        self,
        data_to_update: Dict[str, List[Dict[str, str]]],
    ) -> None:
        print("Updating assets historical prices...")
        db = self.firestore_connection

        batch = db.batch()

        for asset_id, values in data_to_update.items():
            print(f"Updating assetId: {asset_id}...")
            doc_ref = db.collection("assetsHistoricalPrices").document(asset_id)
            batch.update(doc_ref, {"values": values})

        batch.commit()
        print("Update complete.")
        return

    def remove_asset_collection(self, asset_id: str, collection_path_name: str) -> None:
        print(f"Removing {collection_path_name} from assetId: {asset_id}...")
        db = self.firestore_connection

        collection_split_path = collection_path_name.split("/")
        document_name = collection_split_path.pop()

        doc_ref = db.collection("assets").document(asset_id)
        for collection in collection_split_path:
            doc_ref = doc_ref.collection(collection)

        doc_ref.document(document_name).delete()

        print("Remove complete.")
        return

    def get_spot_operation_by_id(self, spot_operation_id: Union[str, int]) -> gc_firestore.DocumentSnapshot:
        print("Getting spot operation...")
        db = self.firestore_connection

        return db.collection("spotOperations").document(str(spot_operation_id)).get()

    def update_spot_operations_external_id(
        self,
        spot_operation_id: Union[str, int],
        spot_operation_data: SpotOperationData,
        skip_ruts: List[str] = None,
        include_ruts: List[str] = None,
        skip_external_ids: List[str] = None,
        include_external_ids: List[str] = None,
    ) -> SpotOperationData:
        skip_ruts = skip_ruts or []
        include_ruts = include_ruts or []
        skip_external_ids = skip_external_ids or []
        include_external_ids = include_external_ids or []

        print("Updating spot operations external id...")
        new_spot_operation_detail = []
        counter = 0  # just because
        spot_operation_id_ = str(spot_operation_id)

        for spot_operation_detail in spot_operation_data.spotOperations:
            if skip_ruts and spot_operation_detail.rut in skip_ruts:
                new_spot_operation_detail.append(spot_operation_detail)
                continue

            if include_ruts and spot_operation_detail.rut not in include_ruts:
                new_spot_operation_detail.append(spot_operation_detail)
                continue

            if skip_external_ids and spot_operation_detail.externalId in skip_external_ids:
                new_spot_operation_detail.append(spot_operation_detail)
                continue

            if include_external_ids and spot_operation_detail.externalId not in include_external_ids:
                new_spot_operation_detail.append(spot_operation_detail)
                continue

            spot_operation_detail.externalId = f"{spot_operation_id_}{str(counter).zfill(2)}"
            new_spot_operation_detail.append(spot_operation_detail)
            counter += 1
            if counter > 99:
                spot_operation_id_ = spot_operation_id_[1:]

        db = self.firestore_connection
        doc_ref = db.collection("spotOperations").document(str(spot_operation_id))
        doc_ref.update({"spotOperations": list(map(lambda x: x.serialize, new_spot_operation_detail))})

        spot_operation_data.spotOperations = new_spot_operation_detail
        return spot_operation_data

    def pubsub_call(self, topic_name: str, message: Dict[str, str]) -> None:
        print(f"Calling pubsub {self.racional_app_name} (topic_name: {topic_name}, message: {message})...")

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(self.racional_app_name, topic_name)

        message_data = json.dumps(message).encode("utf-8")
        future = publisher.publish(topic_path, data=message_data)
        future.result()

        print("Pubsub call complete.")
        return

    def get_user_data_by_uid(self, uid: str) -> Optional[Dict]:
        print(f"Getting user data by uid: {uid}...")
        db = self.firestore_connection

        user_data = db.collection("users").document(uid).get()
        return user_data.to_dict()

    def get_bulk_user_data_by_uids(self, uids: List[str], chunk_size: int = 30) -> List[Dict[str, Any]]:
        print(f"Getting bulk user data by uids: {uids}...")
        db = self.firestore_connection

        chunks_ = chunks(lst=uids, chunk_size=chunk_size)
        result = []
        for chunk in chunks_:
            users_data = db.collection("users").where(
                filter=FieldFilter("uid", "in", chunk),
            ).get()
            result.extend(list(map(lambda x: x.to_dict(), users_data)))

        return result

    def get_user_data_by_email(self, email: str) -> Optional[Dict]:
        print(f"Getting user data by email: {email}...")
        db = self.firestore_connection

        user_data = db.collection("users").where("email", "==", email).get()
        user_ = next(iter(user_data), None)
        if not user_:
            return
        return user_.to_dict()

    def add_user_new_email(self, user_uid: str, new_email: str) -> None:
        print(f"Adding new email to user: {user_uid}...")
        db = self.firestore_connection

        doc_ref = db.document(f"users/{user_uid}/emailChanges/{uuid.uuid4()}")
        doc_ref.set({"newEmail": new_email})

        print("Update complete.")
        return

    def get_cash_difference_users(self, less_than_amount: Optional[Number] = None) -> List[Dict[str, str]]:
        print("Getting users...")
        db = self.firestore_connection
        users_ref = db.collection("users").where(
            filter=FieldFilter("cashDifference", "<=", less_than_amount or 0),
        ).get()

        return list(map(lambda x: x.to_dict(), users_ref))

    def get_cash_dw_difference_users(self, less_than_amount: Optional[Number] = None) -> List[Dict[str, str]]:
        print("Getting users...")
        db = self.firestore_connection
        users_ref = db.collection("users").where(
            filter=FieldFilter("cashDifferenceDW", "<=", less_than_amount),
        ).get()

        return list(map(lambda x: x.to_dict(), users_ref))

    def get_cash_usd_users(self, less_than_amount: Optional[Number] = None) -> List[Dict[str, str]]:
        print("Getting users...")
        db = self.firestore_connection
        if less_than_amount is None:
            filter_ = FieldFilter("cashUSD", "!=", 0)
        else:
            filter_ = FieldFilter("cashUSD", "<=", less_than_amount)
        users_ref = db.collection("users").where(
            filter=filter_,
        ).get()

        return list(map(lambda x: x.to_dict(), users_ref))

    def update_spot_operation(self, spot_operation_id: Union[str, int], data: Dict) -> None:
        print("Updating spot operation...")
        db = self.firestore_connection
        doc_ref = db.collection("spotOperations").document(str(spot_operation_id))
        doc_ref.update(data)

        print("Update complete.")
        return

    def get_user_data_by_rut(self, rut: str) -> Optional[Dict]:
        print(f"Getting user data by rut: {rut}...")
        db = self.firestore_connection

        user_data = db.collection("users").where(
            filter=FieldFilter("rut", "==", rut),
        ).get()
        if len(user_data) > 1:
            raise ValueError(f"More than one user with rut {rut}!", [u.id for u in user_data])

        user_ = next(iter(user_data), None)
        if not user_:
            return
        return user_.to_dict()

    def add_user_rut_email(self, user_uid: str, new_rut: str) -> None:
        print(f"Adding new rut to user: {user_uid}...")
        db = self.firestore_connection

        doc_ref = db.document(f"users/{user_uid}/rutChanges/{uuid.uuid4()}")
        doc_ref.set({"correctRut": new_rut})

        print("Update complete.")
        return

    def add_user_modification(self, user_data: Dict) -> None:
        print("Adding user modification...")
        db = self.firestore_connection
        db.collection('userModifications').add(user_data);
        print("Update complete.")

    def update_user_data(self, user_uid: str, data: Dict) -> None:
        print("Updating user data...", data)
        db = self.firestore_connection
        doc_ref = db.collection("users").document(user_uid)
        doc_ref.update(data)

        print("Update complete.")
        return

    def get_no_injected_deposits(self, is_usd: bool = False) -> List[Dict[str, str]]:
        print("Getting no injected deposits...")
        db = self.firestore_connection
        external_injection = "externalInjectionUSD" if is_usd else "externalInjection"

        deposits_ref = db.collection("deposits").where(
            filter=FieldFilter(external_injection, "==", False),
        ).where(
            filter=FieldFilter("status", "==", "complete"),
        ).where(
            filter=FieldFilter("isCashInBuyingPower", "==", True),
        ).get()

        return list(map(lambda x: x.to_dict(), deposits_ref))

    def get_no_injected_withdrawals(self, is_usd: bool = False) -> List[Dict[str, str]]:
        print("Getting no injected withdrawals...")
        db = self.firestore_connection
        external_injection = "externalInjectionUSD" if is_usd else "externalInjection"

        withdrawals_ref = db.collection("withdrawals").where(
            filter=FieldFilter(external_injection, "==", False),
        ).where(
            filter=FieldFilter("status", "==", "complete"),
        ).where(
            filter=FieldFilter("isCashOutBuyingPower", "==", True),
        ).get()

        return list(map(lambda x: x.to_dict(), withdrawals_ref))

    def get_withdrawal_by_id(self, withdrawal_id: str) -> Dict[str, str]:
        print(f"Getting withdrawal {withdrawal_id}...")
        db = self.firestore_connection
        withdrawal_ref = db.collection("withdrawals").document(withdrawal_id).get()

        return withdrawal_ref.to_dict()

    def get_deposit_by_id(self, deposit_id: str) -> Dict[str, str]:
        print(f"Getting deposit {deposit_id}...")
        db = self.firestore_connection
        deposit_ref = db.collection("deposits").document(deposit_id).get()

        return deposit_ref.to_dict()

    def get_deposits_by_users_ids(self, users_ids: List[str], chunk_size=20) -> List[Dict[str, str]]:
        print("Getting deposits...")
        db = self.firestore_connection
        result = []
        for chunk in chunks(lst=users_ids, chunk_size=chunk_size):
            deposits_ref = db.collection("deposits").where(
                filter=FieldFilter("userId", "in", chunk),
            ).get()
            result.extend(list(map(lambda x: x.to_dict(), deposits_ref)))

        print("Deposits:", len(result))
        return result

    def get_withdrawals_by_users_ids(self, users_ids: List[str], chunk_size=20) -> List[Dict[str, str]]:
        print("Getting withdrawals...")
        db = self.firestore_connection
        result = []
        for chunk in chunks(lst=users_ids, chunk_size=chunk_size):
            withdrawals_ref = db.collection("withdrawals").where(
                filter=FieldFilter("userId", "in", chunk),
            ).get()
            result.extend(list(map(lambda x: x.to_dict(), withdrawals_ref)))

        print("Withdrawals:", len(result))
        return result

    def save_dividends_usd_data_by_user_id_and_execution_date(
        self,
        user_id: str,
        execution_date: str,
        data: Dict[str, str],
    ) -> None:
        print(f"Saving dividends usd data: users/{user_id}/dividendsUSD/{execution_date}...")
        db = self.firestore_connection
        doc_ref = db.document(f"users/{user_id}/dividendsUSD/{execution_date}")
        doc_ref.set(data)

        print("Update complete.")
        return
