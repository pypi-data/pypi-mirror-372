"""
This module provides an ApiClient class and utility functions for
interacting with the Energis Cloud API, including asset management,
metric queries, and data retrieval for energy-related assets.
"""

import datetime as dt
import sys

import pandas as pd
import pytz
import requests
from loguru import logger


def split_list(lst, chunk_size):
    return [lst[i: i + chunk_size] for i in range(0, len(lst), chunk_size)]


def toDateTimeIsoFormatString(
    dt_value,
    dt_tz=pytz.timezone("Europe/Brussels")
):

    if isinstance(dt_value, dt.datetime):
        pass
    elif isinstance(dt_value, dt.date):
        logger.warning("the datetime value is a date instance")
    else:
        logger.error(
            f"datetime value must be a datetime instance not {type(dt_value)}"
        )
        sys.exit(1)

    if dt_value.tzinfo is None or dt_value.tzinfo.utcoffset(dt_value) is None:
        dt_value_local = dt_tz.localize(dt_value)
        dt_value_utc = dt_value_local.astimezone(pytz.utc)
        dt_value_naive = dt_value_utc.replace(tzinfo=None)
    else:
        dt_value_utc = dt_value.astimezone(pytz.utc)
        dt_value_naive = dt_value_utc.replace(tzinfo=None)

    dateTimeIsoFormat = "%Y-%m-%dT%H:%M:%SZ"
    return dt.datetime.strftime(dt_value_naive, dateTimeIsoFormat)


class ApiClient:
    def __init__(self, api_key, env_url=None) -> None:
        self.env_url = env_url
        self.api_key = api_key
        self.headers = {"X-Api-Key": api_key}
        if self.env_url and not self.env_url[-1] == "/":
            raise Exception(
                "The environment url must be ended with a forward slash"
            )
        if not self.env_url:
            raise Exception(
                "The env_url is missing, please provide the env_url"
            )

    # def get_site_asset_list_by_assetId(self,api_url, siteID):
    #     if api_url.startswith("/"):
    #         print("api url should no start with a forward slash")
    #     url = self.env_url + api_url
    #     r_entity = requests.get(
    #         url + f"{siteID}",
    #         headers=self.headers,
    #         verify=False
    #     ).json()
    #     return r_entity
    # =============== General POST Request ============
    def post_request(self, api_url, message):
        """
        api_url: str
            api url
        message: dict
            message to be sent to the server
        """
        url = self.env_url + api_url
        r_entity = requests.post(
            url,
            headers=self.headers,
            json=message,
            verify=False
        )
        return r_entity

    # =============== General GET Request ========
    def get_request(self, api_url, message):
        """
        api_url: str
            api url
        message: dict
            message to be sent to the server
        """
        url = self.env_url + api_url
        r_entity = requests.get(
            url,
            headers=self.headers,
            json=message,
            verify=False
        )
        return r_entity

    # ======================= DATASOURCE =======================
    def get_datasource_list(self):

        api_url = "api/mw/v1/datasource"
        url = self.env_url + api_url
        r_ds = requests.get(url, headers=self.headers, verify=False)
        return r_ds

    def get_datasource_by_ID(self, dsID: int):
        """
        dsID: str or int
            datasource ID
        """
        api_url = f"api/mw/v1/datasource/{dsID}"

        url = self.env_url + api_url
        r_ds = requests.get(url, headers=self.headers, verify=False)

        return r_ds

    def get_datasourceMetrics_by_datasourceId(self, dsID: int):

        r_ds = self.get_datasource_by_ID(dsID)
        datasourceMetrics = r_ds.json()["datasourceMetrics"]
        return datasourceMetrics

    # ===================== METRIC ============================
    def create_or_update_semistatic_metric(
        self,
        assetCode: str,
        externalName: str,
        metricValue: float,
        startDate,
        endDate
    ):
        api_url = "api/mw/v1/metric/semi-static-update"
        url = self.env_url + api_url

        if not (
            isinstance(startDate, dt.datetime) or isinstance(endDate, dt.date)
        ):
            logger.error(
                "startDate must be datetime or "
                f"date instance not {type(startDate)}"
            )
            return 1
        if not (
            isinstance(endDate, dt.datetime) or isinstance(endDate, dt.date)
        ):
            logger.error(
                "endDate must be a datetime or "
                f"date instance not {type(endDate)}"
            )
            return 1
        endDateString = toDateTimeIsoFormatString(endDate)
        startDateString = toDateTimeIsoFormatString(startDate)
        message = {
            "assetCode": assetCode,
            "endDate": endDateString,
            "externalName": externalName,
            "startDate": startDateString,
            "value": metricValue,
        }
        res = requests.post(
            url,
            headers=self.headers,
            json=message,
            verify=False
        )
        # r_data=res.json()
        return res

    def get_the_label_list_given_an_id(self, labelID):
        api_url = f"api/mw/v1/labels/id/{labelID}"
        url = self.env_url + api_url

        r_label = requests.get(url, headers=self.headers, verify=False)
        return r_label

    def update_site_asset(
        self,
        entityID,
        assetCode=None,
        assetName=None,
        parentID=None,
        companyAssetId=2665,
        **kwargs,
    ):
        api_url = f"api/mw/v1/site/{entityID}"
        url = self.env_url + api_url

        message = self.get_site_by_ID(entityID)
        category = kwargs.get("category", None)

        if parentID:
            message["parentId"] = parentID
        if assetName:
            message["name"] = assetName
        if assetCode:
            message["code"] = assetCode
        if category:
            message["category"] = category

        r_entity = requests.put(
            url,
            headers=self.headers,
            json=message,
            verify=False
        )
        return r_entity

    def update_site_entity_asset(
        self,
        entityID,
        assetCode=None,
        assetName=None,
        parentID=None,
        description="",
        companyAssetId=2665,
        **kwargs,
    ):
        api_url = f"api/mw/v1/site-entity/{entityID}"
        url = self.env_url + api_url

        message = self.get_site_entity_by_ID(entityID)
        energyType = kwargs.get("energyType", None)
        category = kwargs.get("category", None)
        categoryId = kwargs.get("categoryId", None)

        if parentID:
            message["parentId"] = parentID
        if description:
            message["description"] = description
        if assetName:
            message["name"] = assetName
        if assetCode:
            message["code"] = assetCode
        if energyType:
            message["energyType"] = energyType
        if category:
            message["category"] = category
        if categoryId:
            message["categoryId"] = categoryId

        # if tags:
        #     tag_list = []
        #     for tag in tags:
        #         tag_instance = self.get_the_label_list_given_an_id(
        #           tag["id"]
        #           ).json()
        #         if not tag_list:
        #             tag_list = tag_instance
        #         else:
        #             tag_list = tag_list + tag_instance
        #     if tag_list:
        #         message["tags"] =  tag_list
        #     print(tag_list)

        r_entity = requests.put(
            url,
            headers=self.headers,
            json=message,
            verify=False
        )
        return r_entity

    def link_tags_to_assets(
        self,
        companyAssetId=2665,
        asset_ids=[],
        link_on_tagids=[],
        link_off_tagids=[]
    ):
        api_url = f"api/v1/asset-tags/apply?{companyAssetId}"
        url = self.env_url + api_url

        message = {
            "assetIds": asset_ids,
            "linkOnTagIds": link_on_tagids,
            "linkOffTagIds": link_off_tagids,
            "newTags": None,
        }
        r_linkTags = requests.post(
            # f"https://equans.energis.cloud/energiscloud-gateway/restful/api/v1/asset-tags/apply?{companyAssetId}",
            url,
            headers=self.headers,
            json=message,
            verify=False,
        )
        return r_linkTags

    def create_site_asset(
        self,
        assetCode,
        assetName,
        parentID,
        description="",
        companyAssetId=2665,
        **kwargs,
    ):
        api_url = "api/mw/v1/site"
        url = self.env_url + api_url

        category = kwargs.get("category", "OFFICE")
        message = {
            "companyAssetId": companyAssetId,
            "code": assetCode,
            "name": assetName,
            "description": description,
            "type": "SITE",
            "categoryId": None,
            "category": category,
            "parentId": parentID,
        }

        if description:
            message["description"] = description

        for k, v in kwargs.items():
            if k not in message.keys():
                message[k] = v

        r_entity = requests.post(
            url,
            headers=self.headers,
            json=message,
            verify=False
        )
        return r_entity

    def create_site_entity_asset(
        self,
        assetCode,
        assetName,
        parentID,
        description="",
        companyAssetId=2665,
        **kwargs,
    ):
        api_url = "api/mw/v1/site-entity"
        url = self.env_url + api_url

        message = {
            "companyAssetId": companyAssetId,
            "code": assetCode,
            "name": assetName,
            "type": "SITE_ENTITY",
            "parentId": parentID,
        }
        if description:
            message["description"] = description
        for k, v in kwargs.items():
            if k not in message.keys():
                message[k] = v

        r_entity = requests.post(
            url,
            headers=self.headers,
            json=message,
            verify=False
        )
        return r_entity

    def copy_energis_asset(
        self,
        org_asset_id,
        copyAssetParentId,
        copyAssetCode=None,
        copyAssetName=None,
        metricClonning=False,
        metricSplitGroups=2,
        **kwargs,
    ):
        # get asset detail from id
        orgAssetDetail = self.get_asset_detail_from_id(org_asset_id)
        # NOTE: should add try except for handling error
        if not copyAssetCode:
            copyAssetCode = orgAssetDetail["code"] + "-Copy"
        if not copyAssetName:
            copyAssetName = orgAssetDetail["name"] + "-Copy"

        if orgAssetDetail["type"] == "SITE":
            siteAssetDetail = self.get_site_by_ID(org_asset_id)
            assetCreation = self.create_site_asset(
                copyAssetCode,
                copyAssetName,
                copyAssetParentId,
                category=siteAssetDetail["category"],
                description=siteAssetDetail["description"],
                box=siteAssetDetail["box"],
                city=siteAssetDetail["city"],
                postalCode=siteAssetDetail["postalCode"],
                street=siteAssetDetail["street"],
                streetNumber=siteAssetDetail["streetNumber"],
                countryCode=siteAssetDetail["countryCode"],
                latitude=siteAssetDetail["latitude"],
                longitude=siteAssetDetail["longitude"],
                notes=siteAssetDetail["notes"],
                regionCode=siteAssetDetail["regionCode"],
            )
            if assetCreation.status_code != 200:
                logger.error(
                    "Error on asset creattion {}: {}".format(
                        assetCreation.status_code, assetCreation.text
                    )
                )
            else:
                logger.info(
                    f"Successful asset creation {assetCreation.json()['id']}"
                )

            tagIds = [tag["id"] for tag in siteAssetDetail["tags"]]

        else:
            siteEntityDetail = self.get_site_entity_by_ID(org_asset_id)
            assetCreation = self.create_site_entity_asset(
                copyAssetCode,
                copyAssetName,
                copyAssetParentId,
                description=siteEntityDetail["description"],
                categoryId=siteEntityDetail["categoryId"],
                calorificPower=siteEntityDetail["calorificPower"],
                capacity=siteEntityDetail["capacity"],
                coefficientOfPerformance=siteEntityDetail[
                    "coefficientOfPerformance"
                ],
                countingUnit=siteEntityDetail["countingUnit"],
                eanCode=siteEntityDetail["eanCode"],
                efficiency=siteEntityDetail["efficiency"],
                energyEfficiencyRatio=siteEntityDetail[
                    "energyEfficiencyRatio"
                ],
                energyType=siteEntityDetail["energyType"],
                energyUnit=siteEntityDetail["energyUnit"],
                energyUsage=siteEntityDetail["energyUsage"],
                energyVector=siteEntityDetail["energyVector"],
                frigorificPowerm=siteEntityDetail["frigorificPowerm"],
                gasLhvHhvConversionFactor=siteEntityDetail[
                    "gasLhvHhvConversionFactor"
                ],
                notes=siteEntityDetail["notes"],
            )
            if assetCreation.status_code != 200:
                logger.error(
                    "Error on asset creattion {}: {}".format(
                        assetCreation.status_code, assetCreation.text
                    )
                )
            else:
                logger.info(
                    f"Successful asset creation {assetCreation.json()['id']}"
                )
            tagIds = [tag["id"] for tag in siteEntityDetail["tags"]]

        tagsLinking = self.link_tags_to_assets(
            asset_ids=[assetCreation.json()["id"]], link_on_tagids=tagIds
        )
        if tagsLinking.status_code != 200:
            logger.error(
                "Error on asset tags linking {}: {}".format(
                    tagsLinking, tagsLinking.text
                )
            )
        else:
            logger.info("Successful tags linking")

        if metricClonning:
            orgAssetMetrics = self.get_metric_list_on_an_asset(org_asset_id)
            metricIds = [metric["id"] for metric in orgAssetMetrics]

            for metricList in split_list(metricIds, metricSplitGroups):
                asset_metric_clonning = self.post_request(
                    "/api/mw/v1/metric/clone",
                    {
                        "assetId": org_asset_id,
                        "destinationAssetIds": [assetCreation.json()["id"]],
                        "skipMetricConfigurationIds": [0],
                        "metricConfigurationIds": metricList,
                        "skipMode": True,
                    },
                )
            if asset_metric_clonning.status_code != 200:
                logger.error(
                    "Error on asset metric clonning {}: {}".format(
                        asset_metric_clonning.status_code,
                        asset_metric_clonning.text
                    )
                )
            else:
                logger.info("Successful asset metric clonning")

    def delete_energis_object_by_Id(self, energisObj, objID):
        api_url = f"api/mw/v1/{energisObj}/{objID}"
        url = self.env_url + api_url
        r_energis = requests.delete(url, headers=self.headers, verify=False)
        return r_energis

    def get_energis_object_list(self, energisObj, **kwargs):
        api_url = f"api/mw/v1/{energisObj}"
        url = self.env_url + api_url

        message = {}

        for k, v in kwargs.items():
            if k not in message.keys():
                print(k, v)
                message[k] = v
        r_energis = requests.get(
            url,
            headers=self.headers,
            json=message,
            verify=False
        )
        return r_energis

    def get_site_asset_list(
        self,
        asset_ids=[],
        ancestor_asset_ids=[],
        embed=[]
    ):
        api_url = "api/mw/v1/site"
        url = self.env_url + api_url

        if any([asset_ids, ancestor_asset_ids, embed]):
            url = url + "?"
        if asset_ids:
            for id in asset_ids:
                if url.endswith("?"):
                    url = url + f"asset-ids={id}"
                else:
                    url = url + f"&asset-ids={id}"

        if ancestor_asset_ids:
            for id in ancestor_asset_ids:
                if url.endswith("?"):
                    url = url + f"ancestor-asset-ids={id}"
                else:
                    url = url + f"&ancestor-asset-ids={id}"

        if embed:
            for embed_str in embed:
                if url.endswith("?"):
                    url = url + f"embed={embed_str}"
                else:
                    url = url + f"&embed={embed_str}"

        r_energis = requests.get(url, headers=self.headers, verify=False)
        return r_energis

    def get_energis_object_by_Id(self, energisObj, objID):
        api_url = f"api/mw/v1/{energisObj}/{objID}"
        url = self.env_url + api_url
        r_energis = requests.get(
            url,
            headers=self.headers,
            verify=False
        ).json()
        return r_energis

    def get_site_entity_by_ID(self, entityID):
        api_url = f"api/mw/v1/site-entity/{entityID}"
        url = self.env_url + api_url
        r_entity = requests.get(url, headers=self.headers, verify=False).json()
        return r_entity

    def get_site_by_ID(self, siteID):
        api_url = f"api/mw/v1/site/{siteID}"
        url = self.env_url + api_url
        r_site = requests.get(url, headers=self.headers, verify=False).json()
        return r_site

    def get_asset_subtree_by_parentID(self, parentID, full_subtree=False):
        api_url = "api/mw/v1/asset/"
        url = self.env_url + api_url
        r_subtree = requests.get(
            url + str(parentID) + "/subtree",
            headers=self.headers,
            verify=False
        ).json()

        while not r_subtree[0]["assetId"] == parentID and not full_subtree:
            r_subtree = r_subtree[0]["contents"]

        return r_subtree

    def get_asset_tree_by_parentID(self, parentID):
        api_url = "api/mw/v1/asset/"
        url = self.env_url + api_url
        r_tree = requests.get(
            url + str(parentID) + "/tree", headers=self.headers, verify=False
        ).json()
        return r_tree

    def get_metric_list_on_an_asset(self, assetId):
        api_url = f"api/mw/v1/metrics/{assetId}"
        url = self.env_url + api_url
        r_metric = requests.get(
            # f"https://equans.energis.cloud/energiscloud-gateway/restful/api/mw/v1/metrics/{assetId}",
            url,
            headers=self.headers,
            verify=False,
        ).json()
        return r_metric

    def get_metric_detail_from_id(self, metricID):
        api_url = f"api/mw/v1/metric/{metricID}"
        url = self.env_url + api_url
        r_metric = requests.get(
            url,
            headers=self.headers,
            verify=False,
        ).json()
        return r_metric

    def search_metric_by_name_on_an_asset(
        self, assetID, search_str, string_exact=False
    ):
        metricListOnAsset = self.get_metric_list_on_an_asset(assetID)
        if string_exact:
            res = [
                el
                for el in metricListOnAsset
                if search_str.lower() == el["externalName"].lower()
            ]
        else:
            res = [
                el
                for el in metricListOnAsset
                if search_str.lower() in el["externalName"].lower()
            ]
        return res

    def get_filtered_assets(
        self,
        tagIds=[],
        assetTypes=[],
        categories=[],
        **kwargs
    ):
        api_url = "api/mw/v1/asset/filter"
        url = self.env_url + api_url

        message = {
            "tagIds": tagIds,
            # "assetTypes" :assetTypes,
            # "categories": categories
        }

        if assetTypes:
            message["assetTypes"] = assetTypes
        if categories:
            message["categories"] = categories

        # for k,v in kwargs.items():
        #     print(k,v)
        #     if not k in message.keys() and v:
        #         message[k] = v

        r_assets = requests.post(
            # "https://equans.energis.cloud/energiscloud-gateway/restful/api/mw/v1/asset/filter",
            url,
            headers=self.headers,
            verify=False,
            json=message,
        )
        return r_assets

    def get_asset_detail_from_id(self, assetID):

        api_url = f"api/mw/v1/asset/{assetID}"
        url = self.env_url + api_url

        r_asset = requests.get(
            # "https://equans.energis.cloud/energiscloud-gateway/restful/api/mw/v1/asset/"
            # + str(assetID),
            url,
            headers=self.headers,
            verify=False,
        ).json()
        return r_asset

    def energis_query(
        self, metricID, date_from, date_to, timestep="FIFTEEN_MINUTE", **kwargs
    ):
        """
        metricID:
        date_from:
        date_to:
        timestep
        There is a limit on number of point could be get 2000
        """

        api_url = "api/mw/v1/metric/query"
        url = self.env_url + api_url

        apiURL = kwargs.get(
            "apiURL",
            # "https://equans.energis.cloud/energiscloud-gateway/restful/api/mw/v1/metric/query",
            url
        )
        counterMetricPeakRemoval = kwargs.get("peak_removal", True)
        tzone_str = kwargs.get("tzone_str", "Europe/Brussels")
        timestep = timestep.upper()

        if not isinstance(
            date_from,
            dt.datetime
        ) and isinstance(
            date_to,
            dt.datetime
        ):
            raise Exception("date_from and date_to must be datime instance")
        if timestep not in ["FIFTEEN_MINUTE", "DAY", "HOUR", "MONTH", "YEAR"]:
            raise Exception(
                "timestep must be either 15min or day or hour or month or year"
            )
        if timestep == "DAY":
            timestepsInSeconds = 24 * 3600
        elif timestep == "FIFTEEN_MINUTE":
            timestepsInSeconds = 15 * 60
        elif timestep == "MONTH":
            timestepsInSeconds = 24 * 3600 * 31
        elif timestep == "YEAR":
            timestepsInSeconds = 24 * 3600 * 366
        else:
            timestepsInSeconds = 3600

        remainDataPointToGet = (
            date_to - date_from
        ).total_seconds() / timestepsInSeconds
        r_df = pd.DataFrame()

        while remainDataPointToGet > 2000:
            body = {
                "counterMetricPeakRemoval": counterMetricPeakRemoval,
                "dateFrom": (
                    date_to - dt.timedelta(seconds=2000 * timestepsInSeconds)
                ).isoformat(),  # [:-3]#+"Z",
                "dateTo": date_to.isoformat(),  # [:-3]#+"Z",
                "granularity": timestep,
                "metricConfigurationId": metricID,
            }
            res = requests.post(
                apiURL,
                headers=self.headers,
                json=body,
                verify=False
            )
            r_data = res.json()

            if "timeValues" in r_data.keys() and r_data["timeValues"]:
                df = pd.DataFrame.from_dict(r_data["timeValues"])
                df["@timestamp"] = pd.to_datetime(
                    df["timestamp"]
                ).dt.tz_convert(
                    tzone_str
                )
                df.set_index("@timestamp", inplace=True)
                df.sort_index(inplace=True)
                df.drop(columns="timestamp", inplace=True)
                if r_df.empty:
                    r_df = df
                else:
                    r_df = pd.concat([r_df, df])
            else:
                print(
                    "no timeserie data for the periode "
                    f"from {date_from} to {date_to}"
                )

            remainDataPointToGet = remainDataPointToGet - 2000
            date_to = date_to - dt.timedelta(seconds=2000 * timestepsInSeconds)

        if remainDataPointToGet > 0:
            body = {
                "counterMetricPeakRemoval": True,
                "dateFrom": date_from.isoformat(),  # [:-3]#+"Z",
                "dateTo": date_to.isoformat(),  # [:-3]#+"Z",
                "granularity": timestep,
                "metricConfigurationId": metricID,
            }
            res = requests.post(
                apiURL,
                headers=self.headers,
                json=body,
                verify=False
            )
            r_data = res.json()

            if "timeValues" in r_data.keys() and r_data["timeValues"]:
                df = pd.DataFrame.from_dict(r_data["timeValues"])
                df["@timestamp"] = pd.to_datetime(
                    df["timestamp"]
                ).dt.tz_convert(
                    tzone_str
                )
                df.set_index("@timestamp", inplace=True)
                df.sort_index(inplace=True)
                df.drop(columns="timestamp", inplace=True)
                if r_df.empty:
                    r_df = df
                else:
                    r_df = pd.concat([r_df, df])
            else:
                logger.warning(
                    "no timeserie data for the periode "
                    f"from {date_from} to {date_to}"
                )

        return r_data, r_df

    def energis_query_batch(
        self,
        metricIDs: list,
        date_from,
        date_to,
        timestep="FIFTEEN_MINUTE",
        **kwargs
    ):

        final_df = pd.DataFrame()

        for metricID in metricIDs:
            _, df = self.energis_query(
                metricID,
                date_from=date_from,
                date_to=date_to,
                timestep=timestep
            )
            df.rename(columns={"value": f"value_{metricID}"}, inplace=True)
            if final_df.empty:
                final_df = df
            else:
                final_df = pd.concat([final_df, df], axis=1)

        return final_df
