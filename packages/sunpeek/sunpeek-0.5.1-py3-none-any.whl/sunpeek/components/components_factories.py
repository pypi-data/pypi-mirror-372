# -*- coding: utf-8 -*-

import datetime as dt
from sunpeek.common.unit_uncertainty import Q
from pint import Quantity
from sunpeek.components.types import Collector, CollectorTypes
from sunpeek.components.iam_methods import IAM_Method


class CollectorSST:
    def __new__(cls, eta0hem: Q, a1: Q, a2: Q, ceff: Q, test_reference_area: Q, gross_length: Q,
                iam_method: IAM_Method, collector_type: CollectorTypes,
                kd=None,
                name: str = None, manufacturer_name: str = None, product_name: str = None, licence_number: str = None,
                area_gr: Q = None, area_ap: Q = None, gross_width: Q = None, gross_height: Q = None,
                description: str = None, certificate_date_issued: dt.datetime = None, certificate_lab: str = None,
                certificate_details: str = None, test_report_id: str = None,
                a8=None, f_prime: Q = None, concentration_ratio: Q = None,
                ):
        test_type = "SST"
        a5 = ceff
        return Collector(
            test_reference_area=test_reference_area, test_type=test_type, gross_length=gross_length, name=name,
            manufacturer_name=manufacturer_name, product_name=product_name,
            test_report_id=test_report_id, licence_number=licence_number,
            certificate_date_issued=certificate_date_issued, certificate_lab=certificate_lab,
            certificate_details=certificate_details, collector_type=collector_type,
            area_gr=area_gr, area_ap=area_ap, gross_width=gross_width,
            gross_height=gross_height, a1=a1, a2=a2, a5=a5, a8=a8, kd=kd, eta0hem=eta0hem,
            iam_method=iam_method, f_prime=f_prime, concentration_ratio=concentration_ratio)


class CollectorQDT:
    def __new__(cls, eta0b: Quantity, a1: Quantity, a2: Q, a5: Q, kd: Q, test_reference_area: str, gross_length: Q,
                iam_method: IAM_Method, collector_type: CollectorTypes,
                name: str = None, manufacturer_name: str = None, product_name: str = None, licence_number: str = None,
                area_gr: Q = None, area_ap: Q = None, gross_width: Q = None, gross_height: Q = None,
                description: str = None, certificate_date_issued: dt.datetime = None, certificate_lab: str = None,
                certificate_details: str = None, test_report_id: str = None,
                a8=None, f_prime: Q = None, concentration_ratio: Q = None,
                ):
        test_type = "QDT"
        return Collector(
            test_reference_area=test_reference_area, test_type=test_type, gross_length=gross_length, name=name,
            manufacturer_name=manufacturer_name, product_name=product_name,
            test_report_id=test_report_id, licence_number=licence_number,
            certificate_date_issued=certificate_date_issued,
            certificate_lab=certificate_lab, certificate_details=certificate_details, collector_type=collector_type,
            area_gr=area_gr, area_ap=area_ap, gross_width=gross_width, gross_height=gross_height,
            a1=a1, a2=a2, a5=a5, a8=a8, kd=kd, eta0b=eta0b,
            iam_method=iam_method, f_prime=f_prime, concentration_ratio=concentration_ratio)
