from uuid import UUID
import re
import ipaddress

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import Optional, List, Dict, Self
from datetime import datetime, time
from backend.app.enums.tipo_dia import TipoDiaEnum


# Valid day range (1=Monday, 7=Sunday, ISO week day format)
VALID_DAY_MIN = 1
VALID_DAY_MAX = 7

# Time format pattern HH:MM (24-hour format)
TIME_PATTERN = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')


def _parse_time(time_str: str) -> time:
    """Parse a time string in HH:MM format to a time object."""
    match = TIME_PATTERN.match(time_str)
    if not match:
        raise ValueError(
            f"'{time_str}' nao esta no formato HH:MM valido (00:00-23:59)"
        )
    return time(int(match.group(1)), int(match.group(2)))


def _validate_time_range(inicio: str, fim: str) -> None:
    """Validate that inicio < fim for a time range."""
    start_time = _parse_time(inicio)
    end_time = _parse_time(fim)

    if start_time >= end_time:
        raise ValueError(
            f"Horario de inicio ({inicio}) deve ser anterior ao horario de fim ({fim})"
        )


def _validate_ip_or_cidr(ip: str) -> str:
    """Validate IPv4, IPv6 address or CIDR notation."""
    ip = ip.strip()
    try:
        # Try as individual IP first
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        pass

    # Try as CIDR network
    try:
        net = ipaddress.ip_network(ip, strict=False)
    except ValueError:
        raise ValueError(
            f"'{ip}' nao e um endereco IP ou bloco CIDR valido"
        )

    # Limit CIDR to /24 (256 addresses max)
    if net.num_addresses > 256:
        raise ValueError(
            f"Bloco CIDR '{ip}' muito grande ({net.num_addresses} enderecos). Maximo permitido: /24 (256 enderecos)"
        )
    return ip


def _expand_ip_network(network: str) -> List[str]:
    """Expand a CIDR network into individual IP addresses."""
    net = ipaddress.ip_network(network, strict=False)
    # Limit to /24 networks (256 IPs) to prevent abuse
    if net.num_addresses > 256:
        raise ValueError(
            f"Bloco de IP muito grande ({net.num_addresses} enderecos). Maximo permitido: /24 (256 enderecos)"
        )
    return [str(ip) for ip in net.hosts()]  # hosts() excludes network and broadcast addresses


class RegraAcessoIpsBase(BaseModel):
    empresa_id: UUID
    grupo_id: UUID
    ip_addresses: List[str]  # Lista de IPs ou blocos CIDR
    tipo_dia: TipoDiaEnum
    dias_especificos: Optional[List[int]] = None
    horarios: List[Dict]   # ex: [{"inicio": "08:00", "fim": "18:00"}]
    bloquear_em_feriado: Optional[bool] = False
    ativo: Optional[bool] = True

    @model_validator(mode="after")
    def validar_dias(self) -> Self:
        """dias_especificos é obrigatório quando tipo_dia = 'especificos'"""
        if self.tipo_dia == TipoDiaEnum.especificos and not self.dias_especificos:
            raise ValueError("dias_especificos é obrigatório quando tipo_dia = 'especificos'")
        return self

    @field_validator("ip_addresses")
    @classmethod
    def validar_ip_addresses(cls, v: List[str]) -> List[str]:
        """Validate that all IPs/CIDRs in the list are valid."""
        if not v or len(v) == 0:
            raise ValueError("Lista de IPs nao pode ser vazia")
        if len(v) > 256:
            raise ValueError("Maximo de 256 IPs por vez")
        validated = []
        for ip in v:
            validated.append(_validate_ip_or_cidr(ip))
        return list(dict.fromkeys(validated))  # Remove duplicates preserving order

    @field_validator("dias_especificos")
    @classmethod
    def validar_dias_range(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """
        Validate that dias_especificos contains valid day values (1-7).

        1=Monday, 2=Tuesday, ..., 7=Sunday (ISO week day format)
        """
        if v is None:
            return v

        for dia in v:
            if not isinstance(dia, int):
                raise ValueError(f"Dia '{dia}' deve ser um numero inteiro")
            if dia < VALID_DAY_MIN or dia > VALID_DAY_MAX:
                raise ValueError(
                    f"Dia '{dia}' invalido. Dias devem estar entre {VALID_DAY_MIN} (Segunda) e {VALID_DAY_MAX} (Domingo)"
                )

        # Remove duplicates and sort
        return sorted(set(v))

    @field_validator("horarios")
    @classmethod
    def validar_horarios(cls, v):
        """
        Validate horarios is a list of time range objects.

        Each object must have 'inicio' and 'fim' in HH:MM format,
        and inicio must be before fim.
        """
        if not v or not isinstance(v, list):
            raise ValueError("horarios deve ser uma lista")

        for idx, item in enumerate(v):
            if not isinstance(item, dict):
                raise ValueError("Cada item de horarios deve ser um objeto JSON")
            if "inicio" not in item or "fim" not in item:
                raise ValueError("Cada horário deve conter 'inicio' e 'fim'")

            inicio = item["inicio"]
            fim = item["fim"]

            # Validate time format (HH:MM)
            if not TIME_PATTERN.match(str(inicio)):
                raise ValueError(
                    f"Horario de inicio '{inicio}' invalido. Use o formato HH:MM (00:00-23:59)"
                )
            if not TIME_PATTERN.match(str(fim)):
                raise ValueError(
                    f"Horario de fim '{fim}' invalido. Use o formato HH:MM (00:00-23:59)"
                )

            # Validate that inicio < fim
            _validate_time_range(inicio, fim)

        return v


class RegraAcessoIpsCreate(RegraAcessoIpsBase):
    """Modelo usado no POST /regras-acesso-ips"""
    pass


class RegraAcessoIpsCreateBulk(BaseModel):
    """Modelo para criação em lote - múltiplos grupos para os mesmos IPs"""
    empresa_id: UUID
    grupo_ids: List[UUID]  # Lista de IDs de grupos
    ip_addresses: List[str]  # Lista de IPs ou blocos CIDR
    tipo_dia: TipoDiaEnum
    dias_especificos: Optional[List[int]] = None
    horarios: List[Dict]
    bloquear_em_feriado: Optional[bool] = False
    ativo: Optional[bool] = True

    @model_validator(mode="after")
    def validar_dias(self) -> Self:
        """dias_especificos é obrigatório quando tipo_dia = 'especificos'"""
        if self.tipo_dia == TipoDiaEnum.especificos and not self.dias_especificos:
            raise ValueError("dias_especificos é obrigatório quando tipo_dia = 'especificos'")
        return self

    @field_validator("ip_addresses")
    @classmethod
    def validar_ip_addresses(cls, v: List[str]) -> List[str]:
        """Validate that all IPs/CIDRs in the list are valid."""
        if not v or len(v) == 0:
            raise ValueError("Lista de IPs nao pode ser vazia")
        if len(v) > 256:
            raise ValueError("Maximo de 256 IPs por vez")
        validated = []
        for ip in v:
            validated.append(_validate_ip_or_cidr(ip))
        return list(dict.fromkeys(validated))

    @field_validator("grupo_ids")
    @classmethod
    def validar_grupo_ids(cls, v: List[UUID]) -> List[UUID]:
        """Validate that at least one grupo_id is provided."""
        if not v or len(v) == 0:
            raise ValueError("Selecione ao menos um grupo")
        return v

    @field_validator("dias_especificos")
    @classmethod
    def validar_dias_range(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is None:
            return v
        for dia in v:
            if not isinstance(dia, int):
                raise ValueError(f"Dia '{dia}' deve ser um numero inteiro")
            if dia < VALID_DAY_MIN or dia > VALID_DAY_MAX:
                raise ValueError(
                    f"Dia '{dia}' invalido. Dias devem estar entre {VALID_DAY_MIN} (Segunda) e {VALID_DAY_MAX} (Domingo)"
                )
        return sorted(set(v))

    @field_validator("horarios")
    @classmethod
    def validar_horarios(cls, v):
        if not v or not isinstance(v, list):
            raise ValueError("horarios deve ser uma lista")
        for item in v:
            if not isinstance(item, dict):
                raise ValueError("Cada item de horarios deve ser um objeto JSON")
            if "inicio" not in item or "fim" not in item:
                raise ValueError("Cada horário deve conter 'inicio' e 'fim'")
            inicio = item["inicio"]
            fim = item["fim"]
            if not TIME_PATTERN.match(str(inicio)):
                raise ValueError(f"Horario de inicio '{inicio}' invalido. Use o formato HH:MM (00:00-23:59)")
            if not TIME_PATTERN.match(str(fim)):
                raise ValueError(f"Horario de fim '{fim}' invalido. Use o formato HH:MM (00:00-23:59)")
            _validate_time_range(inicio, fim)
        return v


class RegraAcessoIpsUpdate(BaseModel):
    ip_addresses: Optional[List[str]] = None  # Permite atualizar os IPs
    tipo_dia: Optional[TipoDiaEnum] = None
    dias_especificos: Optional[List[int]] = None
    horarios: Optional[List[Dict]] = None
    bloquear_em_feriado: Optional[bool] = None
    ativo: Optional[bool] = None

    @field_validator("ip_addresses")
    @classmethod
    def validar_ip_addresses_update(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that all IPs/CIDRs in the list are valid."""
        if v is None:
            return v
        if len(v) == 0:
            raise ValueError("Lista de IPs nao pode ser vazia")
        if len(v) > 256:
            raise ValueError("Maximo de 256 IPs por vez")
        validated = []
        for ip in v:
            validated.append(_validate_ip_or_cidr(ip))
        return list(dict.fromkeys(validated))

    @field_validator("dias_especificos")
    @classmethod
    def validar_dias_range_update(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """
        Validate that dias_especificos contains valid day values (1-7).

        1=Monday, 2=Tuesday, ..., 7=Sunday (ISO week day format)
        """
        if v is None:
            return v

        for dia in v:
            if not isinstance(dia, int):
                raise ValueError(f"Dia '{dia}' deve ser um numero inteiro")
            if dia < VALID_DAY_MIN or dia > VALID_DAY_MAX:
                raise ValueError(
                    f"Dia '{dia}' invalido. Dias devem estar entre {VALID_DAY_MIN} (Segunda) e {VALID_DAY_MAX} (Domingo)"
                )

        # Remove duplicates and sort
        return sorted(set(v))

    @field_validator("horarios")
    @classmethod
    def validar_horarios_update(cls, v):
        """
        Validate horarios is a list of time range objects.

        Each object must have 'inicio' and 'fim' in HH:MM format,
        and inicio must be before fim.
        """
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("horarios deve ser uma lista")

        for item in v:
            if "inicio" not in item or "fim" not in item:
                raise ValueError("Cada horário deve conter 'inicio' e 'fim'")

            inicio = item["inicio"]
            fim = item["fim"]

            # Validate time format (HH:MM)
            if not TIME_PATTERN.match(str(inicio)):
                raise ValueError(
                    f"Horario de inicio '{inicio}' invalido. Use o formato HH:MM (00:00-23:59)"
                )
            if not TIME_PATTERN.match(str(fim)):
                raise ValueError(
                    f"Horario de fim '{fim}' invalido. Use o formato HH:MM (00:00-23:59)"
                )

            # Validate that inicio < fim
            _validate_time_range(inicio, fim)

        return v


class RegraAcessoIpsOut(RegraAcessoIpsBase):
    regra_id: UUID
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class RegraAcessoIpsOutWithDetails(RegraAcessoIpsOut):
    """Modelo de saida com detalhes do grupo"""
    grupo_nome: Optional[str] = None
