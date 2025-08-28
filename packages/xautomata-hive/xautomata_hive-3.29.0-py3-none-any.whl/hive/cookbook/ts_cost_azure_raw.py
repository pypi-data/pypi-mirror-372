from hive.api import ApiManager, handling_single_page_methods, warning_wrong_parameters


class TsCostAzureRaw(ApiManager):
    """Class that handles all the XAutomata ts_cost_azure_raw APIs"""

    def ts_cost_azure_raw(self, warm_start: bool = False,
        single_page: bool = False, page_size: int = 5000,
        kwargs: dict = None, **params) -> list:
        """Read Costs

        Args:
            warm_start (bool, optional): salva la risposta in un file e se viene richiamata la stessa funzione con gli stessi argomenti restituisce il contenuto del file. Default to False.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 5000.
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            sort_by (string optional): Stringa separata da virgole di campi su cui ordinare. Si indica uno o piu campi della risposta e si puo chiedere di ottenere i valori di quei campi in ordine ascendente o discendente. Esempio "Customer:Desc". Default to "". - parameter
            null_fields (string optional): additional filter - parameter
            uuid_metric (string optional): additional filter - parameter
            date_start (string optional): additional filter - parameter
            date_end (string optional): additional filter - parameter
            skip (integer optional): numero di oggetti che si vogliono saltare nella risposta. Default to 0. - parameter
            limit (integer optional): numero di oggetti massimi che si vogliono ottenere. Default to 1_000_000. - parameter
            like (boolean optional): Se True, eventuali filtri richiesti dalla API vengono presi come porzioni di testo, se False il matching sul campo dei filtri deve essere esatto. Default to True. - parameter
            join (boolean optional): Se join = true, ogni riga restituita conterra' chiavi aggiuntive che fanno riferimento ad altre entita', con cui la riga ha relazioni 1:1. Default to False - parameter
            count (boolean optional): Se True nel header della risposta e' presente la dimensione massima a db della chiamata fatta, sconsigliabile perche raddoppia il tempo per chiamata. Default to False. - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['sort_by', 'null_fields', 'uuid_metric',
            'date_start', 'date_end', 'skip', 'limit', 'like', 'join', 'count']
        params.get('sort_by'), params.get('null_fields'), params.get(
            'uuid_metric'), params.get('date_start'), params.get('date_end'
            ), params.get('skip'), params.get('limit'), params.get('like'
            ), params.get('join'), params.get('count')
        if not self._silence_warning:
            warning_wrong_parameters(self.ts_cost_azure_raw.__name__,
                params, official_params_list)
        response = self.execute('GET', path=f'/ts_cost_azure_raw/',
            single_page=single_page, page_size=page_size, warm_start=
            warm_start, params=params, **kwargs)
        return response

    def ts_cost_azure_raw_create(self, kwargs: dict = None, **payload) -> list:
        """Create Cost

        Args:
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            tags (array object optional): additional filter - payload
            term (string optional): additional filter - payload
            meterid (string optional): additional filter - payload
            location (string optional): additional filter - payload
            provider (string optional): additional filter - payload
            quantity (number optional): additional filter - payload
            paygprice (number optional): additional filter - payload
            productid (string optional): additional filter - payload
            benefitid (string optional): additional filter - payload
            costinusd (number optional): additional filter - payload
            frequency (string optional): additional filter - payload
            invoiceid (string optional): additional filter - payload
            metername (string optional): additional filter - payload
            unitprice (number optional): additional filter - payload
            resourceid (string optional): additional filter - payload
            chargetype (string optional): additional filter - payload
            costcenter (string optional): additional filter - payload
            productname (string optional): additional filter - payload
            benefitname (string optional): additional filter - payload
            meterregion (string optional): additional filter - payload
            partnername (string optional): additional filter - payload
            publisherid (string optional): additional filter - payload
            customername (string optional): additional filter - payload
            pricingmodel (string optional): additional filter - payload
            resellername (string optional): additional filter - payload
            serviceinfo1 (string optional): additional filter - payload
            serviceinfo2 (string optional): additional filter - payload
            metercategory (string optional): additional filter - payload
            paygcostinusd (number optional): additional filter - payload
            publishername (string optional): additional filter - payload
            publishertype (string optional): additional filter - payload
            resellermpnid (string optional): additional filter - payload
            reservationid (string optional): additional filter - payload
            servicefamily (string optional): additional filter - payload
            unitofmeasure (string optional): additional filter - payload
            subscriptionid (string optional): additional filter - payload
            additionalinfo (array object optional): additional filter - payload
            effectiveprice (number optional): additional filter - payload
            productorderid (string optional): additional filter - payload
            billingcurrency (string optional): additional filter - payload
            consumedservice (string optional): additional filter - payload
            partnertenantid (string optional): additional filter - payload
            pricingcurrency (string optional): additional filter - payload
            reservationname (string optional): additional filter - payload
            billingaccountid (string optional): additional filter - payload
            billingprofileid (string optional): additional filter - payload
            customertenantid (string optional): additional filter - payload
            exchangeratedate (string optional): additional filter - payload
            invoicesectionid (string optional): additional filter - payload
            metersubcategory (string optional): additional filter - payload
            productordername (string optional): additional filter - payload
            resourcelocation (string optional): additional filter - payload
            subscriptionname (string optional): additional filter - payload
            previousinvoiceid (string optional): additional filter - payload
            resourcegroupname (string optional): additional filter - payload
            billingaccountname (string optional): additional filter - payload
            billingprofilename (string optional): additional filter - payload
            invoicesectionname (string optional): additional filter - payload
            billingperiodenddate (string optional): additional filter - payload
            serviceperiodenddate (string optional): additional filter - payload
            costinbillingcurrency (number optional): additional filter - payload
            costinpricingcurrency (number optional): additional filter - payload
            isazurecrediteligible (boolean optional): additional filter - payload
            billingperiodstartdate (string optional): additional filter - payload
            serviceperiodstartdate (string optional): additional filter - payload
            partnerearnedcreditrate (number optional): additional filter - payload
            paygcostinbillingcurrency (number optional): additional filter - payload
            partnerearnedcreditapplied (boolean optional): additional filter - payload
            exchangeratepricingtobilling (number optional): additional filter - payload
            uuid (string required): additional filter - payload
            uuid_metric (string required): additional filter - payload
            date (string required): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['tags', 'term', 'meterid', 'location',
            'provider', 'quantity', 'paygprice', 'productid', 'benefitid',
            'costinusd', 'frequency', 'invoiceid', 'metername', 'unitprice',
            'resourceid', 'chargetype', 'costcenter', 'productname',
            'benefitname', 'meterregion', 'partnername', 'publisherid',
            'customername', 'pricingmodel', 'resellername', 'serviceinfo1',
            'serviceinfo2', 'metercategory', 'paygcostinusd',
            'publishername', 'publishertype', 'resellermpnid',
            'reservationid', 'servicefamily', 'unitofmeasure',
            'subscriptionid', 'additionalinfo', 'effectiveprice',
            'productorderid', 'billingcurrency', 'consumedservice',
            'partnertenantid', 'pricingcurrency', 'reservationname',
            'billingaccountid', 'billingprofileid', 'customertenantid',
            'exchangeratedate', 'invoicesectionid', 'metersubcategory',
            'productordername', 'resourcelocation', 'subscriptionname',
            'previousinvoiceid', 'resourcegroupname', 'billingaccountname',
            'billingprofilename', 'invoicesectionname',
            'billingperiodenddate', 'serviceperiodenddate',
            'costinbillingcurrency', 'costinpricingcurrency',
            'isazurecrediteligible', 'billingperiodstartdate',
            'serviceperiodstartdate', 'partnerearnedcreditrate',
            'paygcostinbillingcurrency', 'partnerearnedcreditapplied',
            'exchangeratepricingtobilling', 'uuid', 'uuid_metric', 'date']
        payload.get('tags'), payload.get('term'), payload.get('meterid'
            ), payload.get('location'), payload.get('provider'), payload.get(
            'quantity'), payload.get('paygprice'), payload.get('productid'
            ), payload.get('benefitid'), payload.get('costinusd'), payload.get(
            'frequency'), payload.get('invoiceid'), payload.get('metername'
            ), payload.get('unitprice'), payload.get('resourceid'
            ), payload.get('chargetype'), payload.get('costcenter'
            ), payload.get('productname'), payload.get('benefitname'
            ), payload.get('meterregion'), payload.get('partnername'
            ), payload.get('publisherid'), payload.get('customername'
            ), payload.get('pricingmodel'), payload.get('resellername'
            ), payload.get('serviceinfo1'), payload.get('serviceinfo2'
            ), payload.get('metercategory'), payload.get('paygcostinusd'
            ), payload.get('publishername'), payload.get('publishertype'
            ), payload.get('resellermpnid'), payload.get('reservationid'
            ), payload.get('servicefamily'), payload.get('unitofmeasure'
            ), payload.get('subscriptionid'), payload.get('additionalinfo'
            ), payload.get('effectiveprice'), payload.get('productorderid'
            ), payload.get('billingcurrency'), payload.get('consumedservice'
            ), payload.get('partnertenantid'), payload.get('pricingcurrency'
            ), payload.get('reservationname'), payload.get('billingaccountid'
            ), payload.get('billingprofileid'), payload.get('customertenantid'
            ), payload.get('exchangeratedate'), payload.get('invoicesectionid'
            ), payload.get('metersubcategory'), payload.get('productordername'
            ), payload.get('resourcelocation'), payload.get('subscriptionname'
            ), payload.get('previousinvoiceid'), payload.get(
            'resourcegroupname'), payload.get('billingaccountname'
            ), payload.get('billingprofilename'), payload.get(
            'invoicesectionname'), payload.get('billingperiodenddate'
            ), payload.get('serviceperiodenddate'), payload.get(
            'costinbillingcurrency'), payload.get('costinpricingcurrency'
            ), payload.get('isazurecrediteligible'), payload.get(
            'billingperiodstartdate'), payload.get('serviceperiodstartdate'
            ), payload.get('partnerearnedcreditrate'), payload.get(
            'paygcostinbillingcurrency'), payload.get(
            'partnerearnedcreditapplied'), payload.get(
            'exchangeratepricingtobilling'), payload.get('uuid'), payload.get(
            'uuid_metric'), payload.get('date')
        if not self._silence_warning:
            warning_wrong_parameters(self.ts_cost_azure_raw_create.__name__,
                payload, official_payload_list)
        response = self.execute('POST', path=f'/ts_cost_azure_raw/',
            payload=payload, **kwargs)
        return response

    def ts_cost_azure_raw_put(self, uuid: str, kwargs: dict = None, **payload
        ) -> list:
        """Update Message

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **payload: additional parameters for the API.

        Keyword Args:
            tags (array object optional): additional filter - payload
            term (string optional): additional filter - payload
            meterid (string optional): additional filter - payload
            location (string optional): additional filter - payload
            provider (string optional): additional filter - payload
            quantity (number optional): additional filter - payload
            paygprice (number optional): additional filter - payload
            productid (string optional): additional filter - payload
            benefitid (string optional): additional filter - payload
            costinusd (number optional): additional filter - payload
            frequency (string optional): additional filter - payload
            invoiceid (string optional): additional filter - payload
            metername (string optional): additional filter - payload
            unitprice (number optional): additional filter - payload
            resourceid (string optional): additional filter - payload
            chargetype (string optional): additional filter - payload
            costcenter (string optional): additional filter - payload
            productname (string optional): additional filter - payload
            benefitname (string optional): additional filter - payload
            meterregion (string optional): additional filter - payload
            partnername (string optional): additional filter - payload
            publisherid (string optional): additional filter - payload
            customername (string optional): additional filter - payload
            pricingmodel (string optional): additional filter - payload
            resellername (string optional): additional filter - payload
            serviceinfo1 (string optional): additional filter - payload
            serviceinfo2 (string optional): additional filter - payload
            metercategory (string optional): additional filter - payload
            paygcostinusd (number optional): additional filter - payload
            publishername (string optional): additional filter - payload
            publishertype (string optional): additional filter - payload
            resellermpnid (string optional): additional filter - payload
            reservationid (string optional): additional filter - payload
            servicefamily (string optional): additional filter - payload
            unitofmeasure (string optional): additional filter - payload
            subscriptionid (string optional): additional filter - payload
            additionalinfo (array object optional): additional filter - payload
            effectiveprice (number optional): additional filter - payload
            productorderid (string optional): additional filter - payload
            billingcurrency (string optional): additional filter - payload
            consumedservice (string optional): additional filter - payload
            partnertenantid (string optional): additional filter - payload
            pricingcurrency (string optional): additional filter - payload
            reservationname (string optional): additional filter - payload
            billingaccountid (string optional): additional filter - payload
            billingprofileid (string optional): additional filter - payload
            customertenantid (string optional): additional filter - payload
            exchangeratedate (string optional): additional filter - payload
            invoicesectionid (string optional): additional filter - payload
            metersubcategory (string optional): additional filter - payload
            productordername (string optional): additional filter - payload
            resourcelocation (string optional): additional filter - payload
            subscriptionname (string optional): additional filter - payload
            previousinvoiceid (string optional): additional filter - payload
            resourcegroupname (string optional): additional filter - payload
            billingaccountname (string optional): additional filter - payload
            billingprofilename (string optional): additional filter - payload
            invoicesectionname (string optional): additional filter - payload
            billingperiodenddate (string optional): additional filter - payload
            serviceperiodenddate (string optional): additional filter - payload
            costinbillingcurrency (number optional): additional filter - payload
            costinpricingcurrency (number optional): additional filter - payload
            isazurecrediteligible (boolean optional): additional filter - payload
            billingperiodstartdate (string optional): additional filter - payload
            serviceperiodstartdate (string optional): additional filter - payload
            partnerearnedcreditrate (number optional): additional filter - payload
            paygcostinbillingcurrency (number optional): additional filter - payload
            partnerearnedcreditapplied (boolean optional): additional filter - payload
            exchangeratepricingtobilling (number optional): additional filter - payload

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_payload_list = ['tags', 'term', 'meterid', 'location',
            'provider', 'quantity', 'paygprice', 'productid', 'benefitid',
            'costinusd', 'frequency', 'invoiceid', 'metername', 'unitprice',
            'resourceid', 'chargetype', 'costcenter', 'productname',
            'benefitname', 'meterregion', 'partnername', 'publisherid',
            'customername', 'pricingmodel', 'resellername', 'serviceinfo1',
            'serviceinfo2', 'metercategory', 'paygcostinusd',
            'publishername', 'publishertype', 'resellermpnid',
            'reservationid', 'servicefamily', 'unitofmeasure',
            'subscriptionid', 'additionalinfo', 'effectiveprice',
            'productorderid', 'billingcurrency', 'consumedservice',
            'partnertenantid', 'pricingcurrency', 'reservationname',
            'billingaccountid', 'billingprofileid', 'customertenantid',
            'exchangeratedate', 'invoicesectionid', 'metersubcategory',
            'productordername', 'resourcelocation', 'subscriptionname',
            'previousinvoiceid', 'resourcegroupname', 'billingaccountname',
            'billingprofilename', 'invoicesectionname',
            'billingperiodenddate', 'serviceperiodenddate',
            'costinbillingcurrency', 'costinpricingcurrency',
            'isazurecrediteligible', 'billingperiodstartdate',
            'serviceperiodstartdate', 'partnerearnedcreditrate',
            'paygcostinbillingcurrency', 'partnerearnedcreditapplied',
            'exchangeratepricingtobilling']
        payload.get('tags'), payload.get('term'), payload.get('meterid'
            ), payload.get('location'), payload.get('provider'), payload.get(
            'quantity'), payload.get('paygprice'), payload.get('productid'
            ), payload.get('benefitid'), payload.get('costinusd'), payload.get(
            'frequency'), payload.get('invoiceid'), payload.get('metername'
            ), payload.get('unitprice'), payload.get('resourceid'
            ), payload.get('chargetype'), payload.get('costcenter'
            ), payload.get('productname'), payload.get('benefitname'
            ), payload.get('meterregion'), payload.get('partnername'
            ), payload.get('publisherid'), payload.get('customername'
            ), payload.get('pricingmodel'), payload.get('resellername'
            ), payload.get('serviceinfo1'), payload.get('serviceinfo2'
            ), payload.get('metercategory'), payload.get('paygcostinusd'
            ), payload.get('publishername'), payload.get('publishertype'
            ), payload.get('resellermpnid'), payload.get('reservationid'
            ), payload.get('servicefamily'), payload.get('unitofmeasure'
            ), payload.get('subscriptionid'), payload.get('additionalinfo'
            ), payload.get('effectiveprice'), payload.get('productorderid'
            ), payload.get('billingcurrency'), payload.get('consumedservice'
            ), payload.get('partnertenantid'), payload.get('pricingcurrency'
            ), payload.get('reservationname'), payload.get('billingaccountid'
            ), payload.get('billingprofileid'), payload.get('customertenantid'
            ), payload.get('exchangeratedate'), payload.get('invoicesectionid'
            ), payload.get('metersubcategory'), payload.get('productordername'
            ), payload.get('resourcelocation'), payload.get('subscriptionname'
            ), payload.get('previousinvoiceid'), payload.get(
            'resourcegroupname'), payload.get('billingaccountname'
            ), payload.get('billingprofilename'), payload.get(
            'invoicesectionname'), payload.get('billingperiodenddate'
            ), payload.get('serviceperiodenddate'), payload.get(
            'costinbillingcurrency'), payload.get('costinpricingcurrency'
            ), payload.get('isazurecrediteligible'), payload.get(
            'billingperiodstartdate'), payload.get('serviceperiodstartdate'
            ), payload.get('partnerearnedcreditrate'), payload.get(
            'paygcostinbillingcurrency'), payload.get(
            'partnerearnedcreditapplied'), payload.get(
            'exchangeratepricingtobilling')
        if not self._silence_warning:
            warning_wrong_parameters(self.ts_cost_azure_raw_put.__name__,
                payload, official_payload_list)
        response = self.execute('PUT', path=f'/ts_cost_azure_raw/{uuid}',
            payload=payload, **kwargs)
        return response

    def ts_cost_azure_raw_delete(self, uuid: str, kwargs: dict = None) -> list:
        """Delete Cost

        Args:
            uuid (str, required): uuid
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('DELETE', path=f'/ts_cost_azure_raw/{uuid}',
            **kwargs)
        return response

    def ts_cost_azure_raw_metric_delete(self, uuid_metric: str,
        kwargs: dict = None, **params) -> list:
        """Delete For Uuid Metric

        Args:
            uuid_metric (str, required): uuid_metric
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.ts_cost_azure_raw_metric_delete.
                __name__, params, official_params_list)
        response = self.execute('DELETE', path=
            f'/ts_cost_azure_raw/metric/{uuid_metric}/', params=params, **
            kwargs)
        return response

    def ts_cost_azure_raw_probe_delete(self, uuid_probe: str,
        kwargs: dict = None, **params) -> list:
        """Delete For Uuid Probe And Date Range

        Args:
            uuid_probe (str, required): uuid_probe
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            tenant_id (string optional): additional filter - parameter
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['tenant_id', 'date_start', 'date_end']
        params.get('tenant_id'), params.get('date_start'), params.get(
            'date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.ts_cost_azure_raw_probe_delete.
                __name__, params, official_params_list)
        response = self.execute('DELETE', path=
            f'/ts_cost_azure_raw/probe/{uuid_probe}/', params=params, **kwargs)
        return response

    def ts_cost_azure_raw_create_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Create Ts Service Value

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
           {
            "tags": "array object", optional
            "term": "string", optional
            "meterid": "string", optional
            "location": "string", optional
            "provider": "string", optional
            "quantity": "number", optional
            "paygprice": "number", optional
            "productid": "string", optional
            "benefitid": "string", optional
            "costinusd": "number", optional
            "frequency": "string", optional
            "invoiceid": "string", optional
            "metername": "string", optional
            "unitprice": "number", optional
            "resourceid": "string", optional
            "chargetype": "string", optional
            "costcenter": "string", optional
            "productname": "string", optional
            "benefitname": "string", optional
            "meterregion": "string", optional
            "partnername": "string", optional
            "publisherid": "string", optional
            "customername": "string", optional
            "pricingmodel": "string", optional
            "resellername": "string", optional
            "serviceinfo1": "string", optional
            "serviceinfo2": "string", optional
            "metercategory": "string", optional
            "paygcostinusd": "number", optional
            "publishername": "string", optional
            "publishertype": "string", optional
            "resellermpnid": "string", optional
            "reservationid": "string", optional
            "servicefamily": "string", optional
            "unitofmeasure": "string", optional
            "subscriptionid": "string", optional
            "additionalinfo": "array object", optional
            "effectiveprice": "number", optional
            "productorderid": "string", optional
            "billingcurrency": "string", optional
            "consumedservice": "string", optional
            "partnertenantid": "string", optional
            "pricingcurrency": "string", optional
            "reservationname": "string", optional
            "billingaccountid": "string", optional
            "billingprofileid": "string", optional
            "customertenantid": "string", optional
            "exchangeratedate": "string", optional
            "invoicesectionid": "string", optional
            "metersubcategory": "string", optional
            "productordername": "string", optional
            "resourcelocation": "string", optional
            "subscriptionname": "string", optional
            "previousinvoiceid": "string", optional
            "resourcegroupname": "string", optional
            "billingaccountname": "string", optional
            "billingprofilename": "string", optional
            "invoicesectionname": "string", optional
            "billingperiodenddate": "string", optional
            "serviceperiodenddate": "string", optional
            "costinbillingcurrency": "number", optional
            "costinpricingcurrency": "number", optional
            "isazurecrediteligible": "boolean", optional
            "billingperiodstartdate": "string", optional
            "serviceperiodstartdate": "string", optional
            "partnerearnedcreditrate": "number", optional
            "paygcostinbillingcurrency": "number", optional
            "partnerearnedcreditapplied": "boolean", optional
            "exchangeratepricingtobilling": "number", optional
            "uuid": "string", required
            "uuid_metric": "string", required
            "date": "string", required
           }
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/ts_cost_azure_raw/bulk/create/', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def ts_cost_azure_raw_delete_bulk(self, payload: list,
        single_page: bool = False, page_size: int = 50, kwargs: dict = None
        ) -> list:
        """Bulk Delete Anomalies

        Args:
            payload (list[dict], optional): List dict to create.
            single_page (bool, optional): se False la risposta viene ottenuta a step per non appesantire le API. Default to False.
            page_size (int, optional): Numero di oggetti per pagina se single_page == False. Default to 50.
            kwargs (dict, optional): additional parameters for execute. Default to None.

        Examples:
            payload = 
          [
            "uuid": "str", required
          ]

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        response = self.execute('POST', path=
            f'/ts_cost_azure_raw/bulk/delete/', single_page=single_page,
            page_size=page_size, payload=payload, **kwargs)
        return response

    def ts_cost_azure_raw_compute_probe_create(self, uuid_probe: str,
        kwargs: dict = None, **params) -> list:
        """Bulk Transform Cost

        Args:
            uuid_probe (str, required): uuid_probe
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            tenant_id (string optional): additional filter - parameter
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['tenant_id', 'date_start', 'date_end']
        params.get('tenant_id'), params.get('date_start'), params.get(
            'date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                ts_cost_azure_raw_compute_probe_create.__name__, params,
                official_params_list)
        response = self.execute('POST', path=
            f'/ts_cost_azure_raw/compute/probe/{uuid_probe}/', params=
            params, **kwargs)
        return response

    def ts_cost_azure_raw_compute_tenant_create(self, uuid_tenant: str,
        kwargs: dict = None, **params) -> list:
        """Bulk Transform Cost Tenant

        Args:
            uuid_tenant (str, required): uuid_tenant
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                ts_cost_azure_raw_compute_tenant_create.__name__, params,
                official_params_list)
        response = self.execute('POST', path=
            f'/ts_cost_azure_raw/compute/tenant/{uuid_tenant}/', params=
            params, **kwargs)
        return response

    def ts_cost_azure_raw_compute_import_tags_tenant_create(self,
        uuid_tenant: str, kwargs: dict = None, **params) -> list:
        """Bulk Import Tags Tenant

        Args:
            uuid_tenant (str, required): uuid_tenant
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                ts_cost_azure_raw_compute_import_tags_tenant_create.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/ts_cost_azure_raw/compute/import_tags/tenant/{uuid_tenant}',
            params=params, **kwargs)
        return response

    def ts_cost_azure_raw_compute_import_tags_customer_create(self,
        uuid_customer: str, kwargs: dict = None, **params) -> list:
        """Bulk Import Tags Customer

        Args:
            uuid_customer (str, required): uuid_customer
            kwargs (dict, optional): additional parameters for execute. Default to None.
            **params: additional parameters for the API.

        Keyword Args:
            date_start (string required): additional filter - parameter
            date_end (string required): additional filter - parameter

        Returns: list"""
        if kwargs is None:
            kwargs = dict()
        official_params_list = ['date_start', 'date_end']
        params.get('date_start'), params.get('date_end')
        if not self._silence_warning:
            warning_wrong_parameters(self.
                ts_cost_azure_raw_compute_import_tags_customer_create.
                __name__, params, official_params_list)
        response = self.execute('POST', path=
            f'/ts_cost_azure_raw/compute/import_tags/customer/{uuid_customer}',
            params=params, **kwargs)
        return response
