"""
SQLAlchemy ORM models for RD Station entities.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ARRAY,
    JSON,
    UUID,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Segmentation(Base):
    """
    ORM model for an RD Station segmentation entity.
    """
    __tablename__ = "rd_segmentations"

    id = Column(String(50), primary_key=True)
    name = Column(String(255))
    standard = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    process_status = Column(String(50))
    links = Column(JSON, default=[])


class SegmentationContact(Base):
    """
    ORM model for a contact within an RD Station segmentation.
    """
    __tablename__ = "rd_segmentation_contacts"

    uuid = Column(UUID, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    last_conversion_date = Column(DateTime)
    created_at = Column(DateTime)
    links = Column(JSON, default=[])
    segmentation_id = Column(String(50), primary_key=True)
    segmentation_name = Column(String(255))
    business_unit = Column(String(50))


class Contact(Base):
    """
    ORM model for an RD Station contact entity.
    """
    __tablename__ = "rd_contacts"

    uuid = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    state = Column(String)
    city = Column(String)
    phone = Column(String)
    mobile_phone = Column(String)
    personal_phone = Column(String)
    tags = Column(ARRAY(Text), default=[])
    legal_bases = Column(JSON, default=[])
    links = Column(JSON, default=[])
    cf_especialidade_ls = Column(String)
    cf_especie_ls = Column(String)
    cf_exame_ls = Column(String)
    cf_especialidade = Column(String)
    cf_especie = Column(String)
    cf_exame = Column(String)
    cf_tipo_de_atendimento = Column(String)
    cf_bu = Column(String)
    cf_utm_source = Column(String)
    cf_utm_medium = Column(String)
    cf_utm_campaign = Column(String)
    cf_id_do_lead = Column(String)
    cf_origem_do_lead = Column(String)
    cf_ultima_atualizacao = Column(String)
    cf_plug_contact_owner = Column(String)
    cf_plug_opportunity_origin = Column(String)
    cf_plug_funnel_stage = Column(String)
    cf_plug_deal_pipeline = Column(String)
    cf_plug_lost_reason = Column(String)


class ContactFunnelStatus(Base):
    """
    ORM model for a contact's funnel status in RD Station.
    """
    __tablename__ = "rd_contact_funnel_status"

    uuid = Column(UUID, primary_key=True)
    lifecycle_stage = Column(String(50))
    opportunity = Column(Boolean)
    contact_owner_email = Column(String(255))
    interest = Column(Integer)
    fit = Column(Integer)
    origin = Column(String(50))


class ConversionEvents(Base):
    """
    ORM model for conversion events associated with a contact in RD Station.
    """
    __tablename__ = "rd_conversion_events"

    uuid = Column(UUID, primary_key=True)
    event_type = Column(String)
    event_family = Column(String)
    event_identifier = Column(String, primary_key=True)
    event_timestamp = Column(DateTime, primary_key=True)
    tags = Column(JSON, default=[])
    payload = Column(JSON, default=[])
    traffic_source = Column(JSON, default=[])
    utm_source = Column(String)
    utm_medium = Column(String)
    utm_campaign = Column(String)
    utm_term = Column(String)
    utm_content = Column(String)


class Lead(Base):
    """
    ORM model for a lead entity in RD Station.
    """
    __tablename__ = "rd_leads"

    uuid = Column(UUID, primary_key=True)
    email = Column(String, primary_key=True)
    name = Column(String)
    unidade = Column(String)
    ano_interesse = Column(String, primary_key=True)
    tags = Column(JSON)
