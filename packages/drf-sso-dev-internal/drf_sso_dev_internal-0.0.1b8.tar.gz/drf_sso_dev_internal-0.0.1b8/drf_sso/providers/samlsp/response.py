import base64
import lxml.etree as ET
from typing import Optional
from datetime import datetime, timezone
from .config import NAMESPACES, SPConfig, IdPConfig
from .xmlsign_utils import XmlSignUtils

class SAMLResponse:
    def __init__(self, b64_response: str, sp: SPConfig, idp: IdPConfig):
        self.sp = sp
        self.idp = idp
        self.xml = base64.b64decode(b64_response.encode())
        self.root = ET.fromstring(self.xml)
        self.assertion = self.root.find(".//saml:Assertion", NAMESPACES)
        self.subject = None
        self.attributes = {}
        self.conditions = {}
        self.session_index = None
        self._parse()

    def _parse(self):
        nameid_elem = self.assertion.find(".//saml:Subject/saml:NameID", NAMESPACES)
        self.subject = nameid_elem.text if nameid_elem is not None else None

        for attr in self.assertion.findall(".//saml:Attribute", NAMESPACES):
            name = attr.attrib.get("Name")
            values = [v.text for v in attr.findall("saml:AttributeValue", NAMESPACES)]
            self.attributes[name] = values if len(values) > 1 else values[0] if values else None

        conditions = self.assertion.find(".//saml:Conditions", NAMESPACES)
        if conditions is not None:
            self.conditions = {
                "not_before": conditions.attrib.get("NotBefore"),
                "not_on_or_after": conditions.attrib.get("NotOnOrAfter")
            }

        authn_stmt = self.assertion.find(".//saml:AuthnStatement", NAMESPACES)
        if authn_stmt is not None:
            self.session_index = authn_stmt.attrib.get("SessionIndex")

    def is_valid(self) -> bool:
        if self.subject is None or not self.attributes:
            return False

        # Signature validation
        if self.sp.want_assertions_signed:
            if not XmlSignUtils.verify(self.xml.decode(), self.idp):
                return False

        now = datetime.now(timezone.utc)
        not_before = self.conditions.get("not_before")
        not_on_or_after = self.conditions.get("not_on_or_after")

        if not_before:
            try:
                if now < datetime.fromisoformat(not_before):
                    return False
            except Exception:
                return False

        if not_on_or_after:
            try:
                if now >= datetime.fromisoformat(not_on_or_after):
                    return False
            except Exception:
                return False

        return True

    def get_attributes(self) -> dict:
        return self.attributes

    def get_subject(self) -> Optional[str]:
        return self.subject

    def get_session_index(self) -> Optional[str]:
        return self.session_index

    def get_conditions(self) -> dict:
        return self.conditions