# -*- coding: utf-8 -*-

from asn1crypto import cms
from asn1crypto import tsp
from asn1crypto import x509
from collective.timestamp import _
from collective.timestamp.interfaces import ITimeStamper
from collective.timestamp.interfaces import ITimestampingSettings
from collective.timestamp.utils import get_timestamp_date_from_tsr_file
from plone import api
from Products.Five.browser import BrowserView
from zope.i18n import translate

import hashlib


RDN_KEY_I18N_MAP = {
    "common_name": _("label_common_name", default="Common Name"),
    "organization_identifier": _(
        "label_organization_identifier", default="Organization Identifier"
    ),
    "organization_name": _("label_organization_name", default="Organization"),
    "organizational_unit_name": _(
        "label_organizational_unit_name", default="Org. Unit"
    ),
    "locality_name": _("label_locality_name", default="Locality"),
    "state_or_province_name": _(
        "label_state_province_name", default="State / Province"
    ),
    "country_name": _("label_country_name", default="Country"),
    "serial_number": _("label_serial_number", default="Serial Number"),
    "email_address": _("label_email_address", default="E-mail"),
    "domain_component": _("label_domain_component", default="Domain"),
}


class TimestampInfo(BrowserView):

    def __init__(self, context, request):
        super().__init__(context, request)
        self.tst_info, self.token_ci, self.signed_data = self._load_tst_info()

    def _load_tst_info(self):
        """
        Return a tsp.TSTInfo instance if the timestamp was granted,
        otherwise None.
        """
        if self.context.timestamp is None:
            return None, None, None
        tsr = self.context.timestamp
        data = tsr.data

        # Decode the outer TimeStampResp
        resp = tsp.TimeStampResp.load(data)
        if resp["status"]["status"].native not in ("granted", "granted_with_mods"):
            return None, None, None

        # Walk down into the CMS Time-Stamp Token
        token_ci = cms.ContentInfo.load(resp["time_stamp_token"].dump())
        signed = token_ci["content"]  # cms.SignedData
        eci = signed["encap_content_info"]  # cms.EncapContentInfo
        content_os = eci["content"]  # OctetString (maybe parsed)

        # If asn1crypto has already parsed the octet-string, use it, otherwise fall back to manual load from bytes.
        try:
            tst_info = content_os.parsed  # preferred path
        except (ValueError, AttributeError):
            raw = content_os.native
            if not isinstance(raw, (bytes, bytearray)):
                raw = content_os.dump()
            tst_info = tsp.TSTInfo.load(raw)

        return tst_info, token_ci, signed  # Return TSTInfo, ContentInfo, SignedData

    def is_timestamped(self):
        handler = ITimeStamper(self.context)
        return handler.is_timestamped()

    def timestamp_date(self):
        tsr_file = self.context.timestamp
        timestamp_date = get_timestamp_date_from_tsr_file(tsr_file.data)
        return timestamp_date.astimezone()

    def timestamp_file_link(self):
        """Return dict {url, label} for the timestamped file."""
        handler = ITimeStamper(self.context)
        field = handler.get_file_field()
        if not field:
            return None
        fieldname = field.fieldname
        value = getattr(self.context, fieldname, None)
        if not value:
            return None
        filename = getattr(value, "filename", None) or "download"
        return {
            "url": f"{self.context.absolute_url()}/@@download/{fieldname}/{filename}",
            "label": filename,
        }

    def timestamp_tsr_link(self):
        """Return dict {url, label} for the TSR file."""
        tsr = getattr(self.context, "timestamp", None)
        if not tsr:
            return None
        filename = getattr(tsr, "filename", None) or "timestamp.tsr"
        return {
            "url": f"{self.context.absolute_url()}/@@download/timestamp/{filename}",
            "label": filename,
        }

    def more_infos_url(self):
        return api.portal.get_registry_record(
            "timestamping_documentation_url",
            interface=ITimestampingSettings,
        )

    def timestamp_policy_oid(self):
        """Policy OID (string, e.g., '1.3.6.1.4.1.…')."""
        if self.tst_info is None:
            return None
        return self.tst_info["policy"].dotted

    def timestamp_serial_number(self):
        """Serial number (int)."""
        if self.tst_info is None:
            return None
        return self.tst_info["serial_number"].native

    def encap_content_type_oid(self):
        """
        OID of the EncapsulatedContentInfo content-type.
        For RFC 3161 tokens this is typically id-ct-TSTInfo = 1.2.840.113549.1.9.16.1.4
        """
        if self.context.timestamp is None:
            return None
        resp = tsp.TimeStampResp.load(self.context.timestamp.data)
        token_ci = cms.ContentInfo.load(resp["time_stamp_token"].dump())
        return token_ci["content"]["encap_content_info"]["content_type"].dotted

    def timestamp_authority(self):
        """Returns a dict with the TSA authority information."""
        if self.tst_info is None:
            return {}

        tsa = self.tst_info["tsa"]

        # Fallback in case the TSA is not a directory name
        if tsa.name != "directory_name":
            req = getattr(self, "request", None)
            return {
                "general_name": {
                    "label": translate(
                        _("label_general_name", default="General Name"),
                        context=req,
                    ),
                    "value": str(tsa.chosen.native),
                }
            }

        name: x509.Name = tsa.chosen

        info = {}
        for rdn in name.chosen:
            for ava in rdn:
                oid = ava["type"].native
                value = ava["value"].native
                label = RDN_KEY_I18N_MAP.get(oid, oid)
                info[oid] = {"label": label, "value": str(value)}

        return info

    def timestamp_precision(self):
        """
        Returns the accuracy of the timestamp in a human-friendly string.

        Examples:
        "1.234 second(s)"
        "0.5 second(s)"
        "0 second (exact)"
        "Not specified"
        """

        if self.tst_info is None:
            return None
        accuracy = self.tst_info.native.get("accuracy", None)
        if not accuracy:
            return _("Not specified")

        seconds = accuracy.get("seconds", 0) or 0
        millis = accuracy.get("millis", 0) or 0
        micros = accuracy.get("micros", 0) or 0

        total_seconds = seconds + millis / 1_000 + micros / 1_000_000

        if total_seconds == 0:
            return _("0 second (exact)")

        if micros:
            fmt = "{:.6f}"
        elif millis:
            fmt = "{:.3f}"
        else:
            fmt = "{:.0f}"

        human = fmt.format(total_seconds).rstrip("0").rstrip(".")
        return _("{} second(s)").format(human)

    def timestamp_protocol(self):
        return "RFC 3161" if self.tst_info is not None else None

    def timestamp_hash(self):
        """
        The message imprint digest (hex-encoded)
        """
        if self.tst_info is None:
            return None
        digest = self.tst_info["message_imprint"]["hashed_message"].native
        # native is bytes
        return digest.hex()

    def timestamp_algorithm(self):
        """
        The hash algorithm used in the message imprint (e.g. 'sha256')
        """
        if self.tst_info is None:
            return None
        alg = self.tst_info["message_imprint"]["hash_algorithm"]["algorithm"].native
        return alg

    def signer_certificate(self):
        """
        Return the asn1crypto.x509.Certificate of the token signer, or None.
        # TODO: https://github.com/wbond/oscrypto has some utilities for this.
        """
        signed = self.signed_data
        if signed is None:
            return None

        try:
            signer_infos = signed["signer_infos"]
            if len(signer_infos) == 0:
                return None
            sid = signer_infos[0]["sid"]
        except Exception:
            return None

        certs_field = signed["certificates"] if "certificates" in signed else []
        if not certs_field:
            return None

        # Match by IssuerAndSerialNumber (most common)
        if sid.name == "issuer_and_serial_number":
            iasn = sid.chosen
            sid_issuer = iasn["issuer"]  # x509.Name
            sid_serial = iasn["serial_number"].native
            for cert_choice in certs_field:
                if cert_choice.name != "certificate":
                    continue
                cert = cert_choice.chosen  # Unwrap CertificateChoices
                tbs = cert["tbs_certificate"]
                if tbs["serial_number"].native != sid_serial:
                    continue
                # Compare issuer by DER to be robust
                if tbs["issuer"].dump() == sid_issuer.dump():
                    return cert
            return None

        # Match by SubjectKeyIdentifier if present
        if sid.name == "subject_key_identifier":
            ski = sid.chosen.native  # bytes
            for cert_choice in certs_field:
                if cert_choice.name != "certificate":
                    continue
                cert = cert_choice.chosen
                try:
                    for ext in cert["tbs_certificate"]["extensions"]:
                        if ext["extn_id"].native == "subject_key_identifier":
                            if ext["extn_value"].native == ski:
                                return cert
                except Exception:
                    continue
            return None
        return None

    def timestamp_signer_subject(self):
        """
        Returns a dict mapping attribute OIDs (e.g., 'common_name') to:
          {'label': <translated label>, 'value': <string>}
        for the signer certificate's *subject*. Empty dict if unavailable.
        """
        cert = self.signer_certificate()
        if cert is None:
            return {}
        subject: x509.Name = cert["tbs_certificate"]["subject"]

        info = {}
        for rdn in subject.chosen:
            for ava in rdn:
                oid = ava["type"].native
                value = ava["value"].native
                label = RDN_KEY_I18N_MAP.get(oid, oid)
                info[oid] = {"label": label, "value": str(value)}
        return info

    @staticmethod
    def _get_ext_value(cert, extn_id):
        """
        Return extension .native value for extn_id or None.
        extn_id examples: 'subject_key_identifier', 'authority_key_identifier'
        """
        try:
            for ext in cert["tbs_certificate"]["extensions"]:
                if ext["extn_id"].native == extn_id:
                    return ext["extn_value"].native
        except Exception:
            return None
        return None

    @classmethod
    def _get_ski(cls, cert):
        """
        Subject Key Identifier bytes, or None if not present.
        """
        val = cls._get_ext_value(cert, "subject_key_identifier")
        return None if val is None else bytes(val)

    @classmethod
    def _get_aki(cls, cert):
        """
        Authority Key Identifier dict (may contain 'key_identifier', 'authority_cert_issuer',
        'authority_cert_serial_number'), or None if not present.
        """
        val = cls._get_ext_value(cert, "authority_key_identifier")
        if val is None:
            return None
        # Normalize key_identifier to bytes if present
        kid = val.get("key_identifier")
        if kid is not None:
            val = dict(val)
            val["key_identifier"] = bytes(kid)
        return val

    @staticmethod
    def _is_self_issued(cert):
        """
        Heuristic: subject == issuer (DER equality).
        Not a cryptographic verification.
        """
        tbs = cert["tbs_certificate"]
        return tbs["subject"].dump() == tbs["issuer"].dump()

    def certificates_in_token(self):
        """
        Return a list[x509.Certificate] of all certificates present in the token.
        TODO: https://github.com/wbond/certvalidator has some utilities for this and does proper validation.
        """
        signed = self.signed_data
        if signed is None:
            return []
        if "certificates" not in signed:
            return []
        certs = signed[
            "certificates"
        ]  # cms.CertificateSet (SequenceOf CertificateChoices)
        return [choice.chosen for choice in certs if choice.name == "certificate"]

    def certificate_chain(self):
        """
        Build a best-effort ordered certificate chain from the signer up to
        the highest ancestor found *within the token's certificate bag*.

        Returns: list[x509.Certificate], where element 0 is the signer.
        Does not do any external fetching or trust evaluation.
        """
        signer = self.signer_certificate()
        if signer is None:
            return []

        all_certs = self.certificates_in_token()
        if not all_certs:
            return [signer]

        # Map SKI -> cert, subjectDN DER -> cert, and (issuerDN DER, serial) -> cert
        ski_map = {}
        subj_map = {}
        serial_map = {}  # (issuer_der, serial_int) -> cert
        for c in all_certs:
            tbs = c["tbs_certificate"]
            subj_der = tbs["subject"].dump()
            iss_der = tbs["issuer"].dump()
            serial = tbs["serial_number"].native
            subj_map[subj_der] = c
            serial_map[(iss_der, serial)] = c
            ski = self._get_ski(c)
            if ski is not None:
                ski_map[ski] = c

        chain = [signer]
        seen = {signer.dump()}

        # Walk upwards using AKI -> SKI if present, else issuer DN (and serial if AKI specifies it)
        current = signer
        for _ in range(len(all_certs)):  # prevent cycles
            tbs = current["tbs_certificate"]
            if self._is_self_issued(current):
                break  # reached (likely) trust anchor within the bag

            aki = self._get_aki(current)
            parent = None

            if aki and aki.get("key_identifier") is not None:
                parent = ski_map.get(aki["key_identifier"])

            if parent is None:
                issuer_der = tbs["issuer"].dump()
                if aki and aki.get("authority_cert_serial_number") is not None:
                    parent = serial_map.get(
                        (issuer_der, aki["authority_cert_serial_number"])
                    )
                if parent is None:
                    parent = subj_map.get(issuer_der)

            if parent is None or parent.dump() in seen:
                break

            chain.append(parent)
            seen.add(parent.dump())
            current = parent

        return chain

    def _name_to_dict(self, name_obj):
        """
        Convert an asn1crypto.x509.Name into a dict similar to timestamp_authority().
        """
        info = {}
        for rdn in name_obj.chosen:
            for ava in rdn:
                oid = ava["type"].native
                value = ava["value"].native
                label = RDN_KEY_I18N_MAP.get(oid, oid)
                info[oid] = {"label": label, "value": str(value)}
        return info

    def certificate_chain_info(self, fingerprint_algorithm="sha256"):
        """
        Return a list of dicts describing the chain.
        Each item has:
          - subject: dict (as in timestamp_authority())
          - issuer: dict
          - serial_number: int
          - fingerprint: hex string (DER over algorithm)
          - self_issued: bool
          - has_ski: bool
          - has_aki: bool
        """
        items = []
        for cert in self.certificate_chain():
            tbs = cert["tbs_certificate"]
            subject = tbs["subject"]
            issuer = tbs["issuer"]
            validity = tbs["validity"]
            fp = hashlib.new(fingerprint_algorithm, cert.dump()).hexdigest()
            not_before = validity["not_before"].native
            not_after = validity["not_after"].native
            items.append(
                {
                    "subject": self._name_to_dict(subject),
                    "issuer": self._name_to_dict(issuer),
                    "serial_number": tbs["serial_number"].native,
                    "fingerprint": fp,
                    "self_issued": self._is_self_issued(cert),
                    "has_ski": self._get_ski(cert) is not None,
                    "has_aki": self._get_aki(cert) is not None,
                    "not_before": not_before,
                    "not_after": not_after,
                }
            )
        return items
