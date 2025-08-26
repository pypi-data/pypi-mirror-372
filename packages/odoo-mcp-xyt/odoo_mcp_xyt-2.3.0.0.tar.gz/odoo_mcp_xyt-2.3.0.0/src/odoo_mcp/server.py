"""
MCP server for Odoo integration

Provides MCP tools and resources for interacting with Odoo ERP systems
"""

import json
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, AsyncIterator, Dict, List, Optional, Union, cast

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field
from zoneinfo import ZoneInfo

from .odoo_client import OdooClient, get_odoo_client


def safe_get_string_field(item: dict, field_name: str) -> Optional[str]:
    """
    Safely get a string field from Odoo record, handling False values.

    Odoo often returns False for empty string fields instead of None or empty string.
    This function converts False to None for optional string fields.
    """
    value = item.get(field_name)
    return value if value not in [False, None] else None


@dataclass
class AppContext:
    """Application context for the MCP server"""

    odoo: OdooClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Application lifespan for initialization and cleanup
    """
    # Initialize Odoo client on startup
    odoo_client = get_odoo_client()

    try:
        yield AppContext(odoo=odoo_client)
    finally:
        # No cleanup needed for Odoo client
        pass


# Create MCP server
mcp = FastMCP(
    "Odoo MCP Server",
    description="MCP Server for interacting with Odoo ERP systems",
    dependencies=["requests"],
    lifespan=app_lifespan,
)


# ----- MCP Resources -----


@mcp.resource(
    "odoo://models", description="List all available models in the Odoo system"
)
def get_models() -> str:
    """Lists all available models in the Odoo system"""
    odoo_client = get_odoo_client()
    models = odoo_client.get_models()
    return json.dumps(models, indent=2)


@mcp.resource(
    "odoo://model/{model_name}",
    description="Get detailed information about a specific model including fields",
)
def get_model_info(model_name: str) -> str:
    """
    Get information about a specific model

    Parameters:
        model_name: Name of the Odoo model (e.g., 'res.partner')
    """
    odoo_client = get_odoo_client()
    try:
        # Get model info
        model_info = odoo_client.get_model_info(model_name)

        # Get field definitions
        fields = odoo_client.get_model_fields(model_name)
        model_info["fields"] = fields

        return json.dumps(model_info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.resource(
    "odoo://record/{model_name}/{record_id}",
    description="Get detailed information of a specific record by ID",
)
def get_record(model_name: str, record_id: str) -> str:
    """
    Get a specific record by ID

    Parameters:
        model_name: Name of the Odoo model (e.g., 'res.partner')
        record_id: ID of the record
    """
    odoo_client = get_odoo_client()
    try:
        record_id_int = int(record_id)
        record = odoo_client.read_records(model_name, [record_id_int])
        if not record:
            return json.dumps(
                {"error": f"Record not found: {model_name} ID {record_id}"}, indent=2
            )
        return json.dumps(record[0], indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.resource(
    "odoo://search/{model_name}/{domain}",
    description="Search for records matching the domain",
)
def search_records_resource(model_name: str, domain: str) -> str:
    """
    Search for records that match a domain

    Parameters:
        model_name: Name of the Odoo model (e.g., 'res.partner')
        domain: Search domain in JSON format (e.g., '[["name", "ilike", "test"]]')
    """
    odoo_client = get_odoo_client()
    try:
        # Parse domain from JSON string
        domain_list = json.loads(domain)

        # Set a reasonable default limit
        limit = 10

        # Perform search_read for efficiency
        results = odoo_client.search_read(model_name, domain_list, limit=limit)

        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# ----- Pydantic models for type safety -----


class DomainCondition(BaseModel):
    """A single condition in a search domain"""

    field: str = Field(description="Field name to search")
    operator: str = Field(
        description="Operator (e.g., '=', '!=', '>', '<', 'in', 'not in', 'like', 'ilike')"
    )
    value: Any = Field(description="Value to compare against")

    def to_tuple(self) -> List:
        """Convert to Odoo domain condition tuple"""
        return [self.field, self.operator, self.value]


class SearchDomain(BaseModel):
    """Search domain for Odoo models"""

    conditions: List[DomainCondition] = Field(
        default_factory=list,
        description="List of conditions for searching. All conditions are combined with AND operator.",
    )

    def to_domain_list(self) -> List[List]:
        """Convert to Odoo domain list format"""
        return [condition.to_tuple() for condition in self.conditions]


class EmployeeSearchResult(BaseModel):
    """Represents a single employee search result."""

    id: int = Field(description="Employee ID")
    name: str = Field(description="Employee name")


class CalendarSearchResult(BaseModel):
    """Represents a single calendar search result."""

    id: int = Field(description="Calendar ID")
    name: str = Field(description="Calendar name")
    start: Optional[str] = Field(default=None, description="开始时间 (YYYY-MM-DD HH:MM:SS)")
    stop: Optional[str] = Field(default=None, description="结束时间 (YYYY-MM-DD HH:MM:SS)")
    allday: Optional[bool] = Field(default=None, description="是否全天事件")
    location: Optional[str] = Field(default=None, description="地点")
    description: Optional[str] = Field(default=None, description="描述")
    partner_ids: Optional[List[str]] = Field(default=None, description="参与者")
    opportunity_id: Optional[int] = Field(default=None, description="关联的商机ID")

class SearchEmployeeResponse(BaseModel):
    """Response model for the search_employee tool."""

    success: bool = Field(description="Indicates if the search was successful")
    result: Optional[List[EmployeeSearchResult]] = Field(
        default=None, description="List of employee search results"
    )
    error: Optional[str] = Field(default=None, description="Error message, if any")


class SearchCalendarResponse(BaseModel):
    """Response model for the search_calendar_by_date tool."""

    success: bool = Field(description="Indicates if the search was successful")
    result: Optional[List[CalendarSearchResult]] = Field(
        default=None, description="List of calendar search results"
    )
    error: Optional[str] = Field(default=None, description="Error message, if any")

class Holiday(BaseModel):
    """Represents a single holiday."""

    display_name: str = Field(description="Display name of the holiday")
    start_datetime: str = Field(description="Start date and time of the holiday")
    stop_datetime: str = Field(description="End date and time of the holiday")
    employee_id: List[Union[int, str]] = Field(
        description="Employee ID associated with the holiday"
    )
    name: str = Field(description="Name of the holiday")
    state: str = Field(description="State of the holiday")


class SearchHolidaysResponse(BaseModel):
    """Response model for the search_holidays tool."""

    success: bool = Field(description="Indicates if the search was successful")
    result: Optional[List[Holiday]] = Field(
        default=None, description="List of holidays found"
    )
    error: Optional[str] = Field(default=None, description="Error message, if any")


# ----- MCP Tools -----


@mcp.tool(description="Execute a custom method on an Odoo model")
def execute_method(
    ctx: Context,
    model: str,
    method: str,
    args: List = None,
    kwargs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a custom method on an Odoo model

    Parameters:
        model: The model name (e.g., 'res.partner')
        method: Method name to execute
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Dictionary containing:
        - success: Boolean indicating success
        - result: Result of the method (if success)
        - error: Error message (if failure)
    """
    odoo = ctx.request_context.lifespan_context.odoo
    try:
        args = args or []
        kwargs = kwargs or {}

        # Special handling for search methods like search, search_count, search_read
        search_methods = ["search", "search_count", "search_read"]
        if method in search_methods and args:
            # Search methods usually have domain as the first parameter
            # args: [[domain], limit, offset, ...] or [domain, limit, offset, ...]
            normalized_args = list(
                args
            )  # Create a copy to avoid affecting the original args

            if len(normalized_args) > 0:
                # Process domain in args[0]
                domain = normalized_args[0]
                domain_list = []

                # Check if domain is wrapped unnecessarily ([domain] instead of domain)
                if (
                    isinstance(domain, list)
                    and len(domain) == 1
                    and isinstance(domain[0], list)
                ):
                    # Case [[domain]] - unwrap to [domain]
                    domain = domain[0]

                # Normalize domain similar to search_records function
                if domain is None:
                    domain_list = []
                elif isinstance(domain, dict):
                    if "conditions" in domain:
                        # Object format
                        conditions = domain.get("conditions", [])
                        domain_list = []
                        for cond in conditions:
                            if isinstance(cond, dict) and all(
                                k in cond for k in ["field", "operator", "value"]
                            ):
                                domain_list.append(
                                    [cond["field"], cond["operator"], cond["value"]]
                                )
                elif isinstance(domain, list):
                    # List format
                    if not domain:
                        domain_list = []
                    elif all(isinstance(item, list) for item in domain) or any(
                        item in ["&", "|", "!"] for item in domain
                    ):
                        domain_list = domain
                    elif len(domain) >= 3 and isinstance(domain[0], str):
                        # Case [field, operator, value] (not [[field, operator, value]])
                        domain_list = [domain]
                elif isinstance(domain, str):
                    # String format (JSON)
                    try:
                        parsed_domain = json.loads(domain)
                        if (
                            isinstance(parsed_domain, dict)
                            and "conditions" in parsed_domain
                        ):
                            conditions = parsed_domain.get("conditions", [])
                            domain_list = []
                            for cond in conditions:
                                if isinstance(cond, dict) and all(
                                    k in cond for k in ["field", "operator", "value"]
                                ):
                                    domain_list.append(
                                        [cond["field"], cond["operator"], cond["value"]]
                                    )
                        elif isinstance(parsed_domain, list):
                            domain_list = parsed_domain
                    except json.JSONDecodeError:
                        try:
                            import ast

                            parsed_domain = ast.literal_eval(domain)
                            if isinstance(parsed_domain, list):
                                domain_list = parsed_domain
                        except:
                            domain_list = []

                # Xác thực domain_list
                if domain_list:
                    valid_conditions = []
                    for cond in domain_list:
                        if isinstance(cond, str) and cond in ["&", "|", "!"]:
                            valid_conditions.append(cond)
                            continue

                        if (
                            isinstance(cond, list)
                            and len(cond) == 3
                            and isinstance(cond[0], str)
                            and isinstance(cond[1], str)
                        ):
                            valid_conditions.append(cond)

                    domain_list = valid_conditions

                # Cập nhật args với domain đã chuẩn hóa
                normalized_args[0] = domain_list
                args = normalized_args

                # Log for debugging
                print(f"Executing {method} with normalized domain: {domain_list}")

        result = odoo.execute_method(model, method, *args, **kwargs)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(name="查询员工", description="Search for employees by name")
def search_employee(
    ctx: Context,
    name: str = Field(description="The name (or part of the name) to search for."),
    limit: int = 20,
) -> SearchEmployeeResponse:
    """
    Search for employees by name using Odoo's name_search method.

    Parameters:
        name: The name (or part of the name) to search for.
        limit: The maximum number of results to return (default 20).

    Returns:
        SearchEmployeeResponse containing results or error information.
    """
    odoo = ctx.request_context.lifespan_context.odoo
    model = "hr.employee"
    method = "name_search"

    args = []
    kwargs = {"name": name, "limit": limit}

    try:
        result = odoo.execute_method(model, method, *args, **kwargs)
        parsed_result = [
            EmployeeSearchResult(id=item[0], name=item[1]) for item in result
        ]
        return SearchEmployeeResponse(success=True, result=parsed_result)
    except Exception as e:
        return SearchEmployeeResponse(success=False, error=str(e))

@mcp.tool(name="查询日历", description="根据日期范围查询当前用户的日历，返回详细时间信息")
def search_calendar_by_date_range(
    ctx: Context,
    start_date: str = Field(description="开始日期，格式为 YYYY-MM-DD"),
    end_date: Optional[str] = Field(default=None, description="结束日期，格式为 YYYY-MM-DD（可选，默认为开始日期）"),
    limit: int = Field(default=50, description="返回的最大结果数（默认50）"),
) -> SearchCalendarResponse:
    """
    Search for current user's calendar events within a date range with detailed time information.

    Parameters:
        start_date: 开始日期，格式为 YYYY-MM-DD
        end_date: 结束日期，格式为 YYYY-MM-DD（可选）
        limit: 返回的最大结果数

    Returns:
        SearchCalendarResponse containing detailed calendar events with time information.
    """
    odoo = ctx.request_context.lifespan_context.odoo
    model = "calendar.event"
    method = "search_read"

    # 如果没有指定结束日期，使用开始日期
    if not end_date:
        end_date = start_date

    # 验证日期格式
    try:
        from datetime import datetime
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return SearchCalendarResponse(success=False, error="日期格式错误，应为 YYYY-MM-DD")

    # 获取当前用户的partner_id
    current_partner_id = None
    try:
        current_user = odoo.execute_method("res.users", "read", [odoo.uid], ["partner_id"])
        if current_user and current_user[0].get("partner_id"):
            current_partner_id = current_user[0]["partner_id"]
            if isinstance(current_partner_id, list):
                current_partner_id = current_partner_id[0]
    except Exception:
        return SearchCalendarResponse(success=False, error="获取当前用户信息失败")

    # 构建查询条件 - 只查询当前用户参与的日历事件
    domain = [
        ["start", ">=", f"{start_date} 00:00:00"],
        ["start", "<=", f"{end_date} 23:59:59"],
        ["partner_ids", "in", [current_partner_id]]
    ]

    kwargs = {
        'fields': [
            'name', 'start', 'stop', 'allday', 'location', 'description',
            'partner_ids', 'opportunity_id', 'res_model', 'res_id'
        ],
        'limit': limit,
        'order': 'start ASC'  # 按开始时间排序
    }

    try:
        # 修复参数传递方式，直接传递domain和kwargs
        result = odoo.execute_method(model, method, domain, **kwargs)

        parsed_result = []
        for item in result:
            # 获取参与者名称
            partner_names = []
            if item.get("partner_ids"):
                try:
                    partner_result = odoo.execute_method(
                        "res.partner",
                        "read",
                        item["partner_ids"],
                        ["name"]
                    )
                    partner_names = [p["name"] for p in partner_result if p.get("name")]
                except Exception:
                    partner_names = []

            # 处理商机ID
            opportunity_id = None
            if item.get("opportunity_id"):
                if isinstance(item["opportunity_id"], list):
                    opportunity_id = item["opportunity_id"][0]
                else:
                    opportunity_id = item["opportunity_id"]

            parsed_result.append(
                CalendarSearchResult(
                    id=item.get("id"),
                    name=item.get("name") or item.get("display_name", ""),
                    start=item.get("start"),
                    stop=item.get("stop"),
                    allday=item.get("allday", False),
                    location=safe_get_string_field(item, "location"),
                    description=safe_get_string_field(item, "description"),
                    partner_ids=partner_names if partner_names else None,
                    opportunity_id=opportunity_id
                )
            )

        return SearchCalendarResponse(success=True, result=parsed_result)
    except Exception as e:
        return SearchCalendarResponse(success=False, error=str(e))

def search_partner_by_name(name: str, limit: int = 10):
    models = endpoint_object()
    uid = get_uid()
    # Search and read
    search_and_read = models.execute_kw(db, uid, password,
                                        'res.partner', 'search_read',
                                        [["&",["is_company","=",True],
                                          ["name","ilike", name],]],
                                        {'fields': ['name', 'email','mobile','opportunity_count' ,'meeting_count','comment'], 'limit': limit})
    return search_and_read

@mcp.tool(description="Search for holidays within a date range")
def search_holidays(
    ctx: Context,
    start_date: str,
    end_date: str,
    employee_id: Optional[int] = None,
) -> SearchHolidaysResponse:
    """
    Searches for holidays within a specified date range.

    Parameters:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        employee_id: Optional employee ID to filter holidays.

    Returns:
        SearchHolidaysResponse:  Object containing the search results.
    """
    odoo = ctx.request_context.lifespan_context.odoo

    # Validate date format using datetime
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return SearchHolidaysResponse(
            success=False, error="Invalid start_date format. Use YYYY-MM-DD."
        )
    try:
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return SearchHolidaysResponse(
            success=False, error="Invalid end_date format. Use YYYY-MM-DD."
        )

    # Calculate adjusted start_date (subtract one day)
    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    adjusted_start_date_dt = start_date_dt - timedelta(days=1)
    adjusted_start_date = adjusted_start_date_dt.strftime("%Y-%m-%d")

    # Build the domain
    domain = [
        "&",
        ["start_datetime", "<=", f"{end_date} 22:59:59"],
        # Use adjusted date
        ["stop_datetime", ">=", f"{adjusted_start_date} 23:00:00"],
    ]
    if employee_id:
        domain.append(
            ["employee_id", "=", employee_id],
        )

    try:
        holidays = odoo.search_read(
            model_name="hr.leave.report.calendar",
            domain=domain,
        )
        parsed_holidays = [Holiday(**holiday) for holiday in holidays]
        return SearchHolidaysResponse(success=True, result=parsed_holidays)

    except Exception as e:
        return SearchHolidaysResponse(success=False, error=str(e))

class PartnerSearchResult(BaseModel):
    """Represents a single partner search result."""
    id: int = Field(description="Partner ID")
    name: str = Field(description="Partner name")
    comment: Optional[str] = Field(default=None, description="Comment")

class SearchPartnerResponse(BaseModel):
    """Response model for the search_partner tool."""
    success: bool = Field(description="Indicates if the search was successful")
    result: Optional[List[PartnerSearchResult]] = Field(
        default=None, description="List of partner search results"
    )
    error: Optional[str] = Field(default=None, description="Error message, if any")

@mcp.tool(name="查询公司伙伴", description="搜索公司类型的伙伴（is_company=True）")
def search_partner(
    ctx: Context,
    limit: int = 5,
) -> SearchPartnerResponse:
    """
    Search for company partners (is_company=True).

    Parameters:
        limit: The maximum number of results to return (default 5).

    Returns:
        SearchPartnerResponse containing results or error information.
    """
    odoo = ctx.request_context.lifespan_context.odoo
    model = "res.partner"
    method = "search_read"
    args = [[["is_company", "=", True]]]
    kwargs = {"fields": ["name", "comment"], "limit": limit}

    try:
        result = odoo.execute_method(model, method, *args, **kwargs)
        parsed_result = [
            PartnerSearchResult(
                id=item.get("id"),
                name=item.get("name"),
                comment=safe_get_string_field(item, "comment"),
            )
            for item in result
        ]
        return SearchPartnerResponse(success=True, result=parsed_result)
    except Exception as e:
        return SearchPartnerResponse(success=False, error=str(e))

class CreateCalendarResponse(BaseModel):
    """Response model for the create_calendar tool."""
    success: bool = Field(description="Indicates if the creation was successful")
    id: Optional[int] = Field(default=None, description="Created calendar event ID")
    error: Optional[str] = Field(default=None, description="Error message, if any")

@mcp.tool(name="创建日历", description="创建一个新的待办活动，关联到商机并生成日历事件")
def create_calendar(
    ctx: Context,
    date: str = Field(description="活动日期，格式为 YYYY-MM-DD"),
    name: str = Field(description="待办活动名称"),
    lead_id: Optional[int] = Field(default=None, description="商机单据ID（关联的商机）"),
    start_time: Optional[str] = Field(default=None, description="开始时间，格式为 HH:MM（如 09:30）"),
    end_time: Optional[str] = Field(default=None, description="结束时间，格式为 HH:MM（如 11:00）"),
    description: Optional[str] = Field(default=None, description="待办事项描述"),
    location: Optional[str] = Field(default=None, description="活动地点"),
    activity_type: Optional[str] = Field(default="todo", description="活动类型：todo(代办), meeting(会议), call(电话), email(邮件)"),
) -> CreateCalendarResponse:
    """
    Create a new todo activity linked to opportunity with calendar event.

    Parameters:
        date: 活动日期，格式为 YYYY-MM-DD
        name: 待办活动名称
        lead_id: 商机单据ID（关联的商机）
        start_time: 开始时间，格式为 HH:MM
        end_time: 结束时间，格式为 HH:MM
        description: 待办事项描述
        location: 活动地点
        activity_type: 活动类型（默认为代办）

    Returns:
        CreateCalendarResponse containing the new activity ID or error information.
    """
    odoo = ctx.request_context.lifespan_context.odoo

    # 校验日期格式
    try:
        event_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return CreateCalendarResponse(success=False, error="日期格式错误，应为 YYYY-MM-DD")

    # 校验时间格式
    start_datetime = None
    end_datetime = None
    is_allday = True

    if start_time or end_time:
        is_allday = False
        try:
            if start_time:
                start_hour, start_minute = map(int, start_time.split(':'))
                start_datetime = event_date.replace(hour=start_hour, minute=start_minute)
            else:
                start_datetime = event_date.replace(hour=9, minute=0)  # 默认9:00开始

            if end_time:
                end_hour, end_minute = map(int, end_time.split(':'))
                end_datetime = event_date.replace(hour=end_hour, minute=end_minute)
            else:
                # 如果只有开始时间，默认持续1小时
                end_datetime = start_datetime.replace(hour=start_datetime.hour + 1)

        except (ValueError, TypeError):
            return CreateCalendarResponse(success=False, error="时间格式错误，应为 HH:MM（如 09:30）")

        # 校验时间逻辑
        if end_datetime <= start_datetime:
            return CreateCalendarResponse(success=False, error="结束时间必须晚于开始时间")

    # 如果提供了商机ID，先获取商机信息
    lead_info = None
    if lead_id:
        try:
            lead_result = odoo.execute_method(
                "crm.lead",
                "read",
                [lead_id],
                ["name", "contact_name", "partner_name", "partner_id", "user_id"]
            )
            if lead_result:
                lead_info = lead_result[0]
            else:
                return CreateCalendarResponse(success=False, error=f"找不到ID为{lead_id}的商机")
        except Exception as e:
            return CreateCalendarResponse(success=False, error=f"获取商机信息失败: {str(e)}")

    # 首先获取或创建活动类型
    activity_type_id = None
    try:
        # 查找"代办"活动类型，如果不存在则使用默认的
        activity_types = odoo.execute_method(
            "mail.activity.type",
            "search_read",
            [["name", "ilike", "代办"]],
            ["id", "name"]
        )
        if activity_types:
            activity_type_id = activity_types[0]["id"]
        else:
            # 如果没有找到"代办"类型，查找"To Do"或其他类似的
            activity_types = odoo.execute_method(
                "mail.activity.type",
                "search_read",
                ["|", ["name", "ilike", "todo"], ["name", "ilike", "to do"]],
                ["id", "name"]
            )
            if activity_types:
                activity_type_id = activity_types[0]["id"]
    except Exception:
        # 如果获取活动类型失败，继续使用默认值
        pass

    # 创建活动（mail.activity）
    activity_model = "mail.activity"
    activity_method = "create"

    # 获取模型ID（mail.activity需要res_model_id而不是res_model字符串）
    res_model_id = None
    if lead_id:
        try:
            model_result = odoo.execute_method(
                "ir.model",
                "search_read",
                [["model", "=", "crm.lead"]],
                ["id"]
            )
            if model_result:
                res_model_id = model_result[0]["id"]
        except Exception:
            return CreateCalendarResponse(success=False, error="获取模型ID失败")

    # 构建活动数据（mail.activity）
    activity_data = {
        "summary": name,
        "note": description or f"待办事项：{name}",
        "date_deadline": date,
    }

    # 只有在有商机ID时才设置模型关联
    if lead_id and res_model_id:
        activity_data["res_model_id"] = res_model_id
        activity_data["res_id"] = lead_id

    # 设置活动类型
    if activity_type_id:
        activity_data["activity_type_id"] = activity_type_id

    # 设置负责人（如果有商机，使用商机的负责人，否则使用当前用户）
    if lead_info and lead_info.get("user_id"):
        user_id = lead_info["user_id"]
        if isinstance(user_id, list):
            user_id = user_id[0]
        activity_data["user_id"] = user_id
    else:
        activity_data["user_id"] = odoo.uid

    # 创建活动
    try:
        activity_id = odoo.execute_method(activity_model, activity_method, [activity_data])
        if isinstance(activity_id, list) and len(activity_id) > 0:
            activity_id = activity_id[0]
    except Exception as e:
        return CreateCalendarResponse(success=False, error=f"创建活动失败: {str(e)}")

    # 创建对应的日历事件（确保在日历中显示）
    calendar_event_id = None

    # 构建日历事件数据
    event_data = {
        "name": f"【待办】{name}",
        "allday": is_allday,
    }

    # 设置时间
    if is_allday:
        event_data["start"] = date
        event_data["stop"] = date
    else:
        event_data["start"] = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        event_data["stop"] = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # 获取当前用户信息并添加为参与者
    participant_ids = []
    try:
        # 获取当前用户的partner_id
        current_user = odoo.execute_method("res.users", "read", [odoo.uid], ["partner_id"])
        if current_user and current_user[0].get("partner_id"):
            current_partner_id = current_user[0]["partner_id"]
            if isinstance(current_partner_id, list):
                current_partner_id = current_partner_id[0]
            participant_ids.append(current_partner_id)
    except Exception:
        # 如果获取当前用户失败，继续创建事件但不添加参与者
        pass

    # 如果关联到商机，添加商机信息
    if lead_info:
        # 关联商机记录 - 使用正确的字段确保可以跳转
        event_data["res_model"] = "crm.lead"
        event_data["res_id"] = lead_id

        # 设置商机关联字段（用于日历中的跳转）
        event_data["opportunity_id"] = lead_id

        # 获取商机的模型ID（用于更准确的关联）
        try:
            lead_model_result = odoo.execute_method(
                "ir.model",
                "search_read",
                [["model", "=", "crm.lead"]],
                ["id"]
            )
            if lead_model_result:
                event_data["res_model_id"] = lead_model_result[0]["id"]
        except Exception:
            # 如果获取失败，继续使用字符串形式
            pass

        # 如果商机有关联的客户，添加为参与者
        if lead_info.get("partner_id"):
            partner_id = lead_info["partner_id"]
            if isinstance(partner_id, list):
                partner_id = partner_id[0]
            # 避免重复添加
            if partner_id not in participant_ids:
                participant_ids.append(partner_id)

        # 增强活动名称，包含商机和客户信息
        contact_info = lead_info.get("contact_name") or lead_info.get("partner_name", "")
        opportunity_name = lead_info.get("name", "")

        if contact_info:
            event_data["name"] = f"【待办】{name} - {contact_info}"
        elif opportunity_name:
            event_data["name"] = f"【待办】{name} - {opportunity_name}"

        # 在描述中添加商机链接信息
        if description and description.strip():
            event_data["description"] = f"待办事项：{name}\n商机：{opportunity_name}\n联系人：{contact_info or '无'}\n\n{description.strip()}"
        else:
            event_data["description"] = f"待办事项：{name}\n商机：{opportunity_name}\n联系人：{contact_info or '无'}"

    # 设置参与者（包括当前用户和商机关联的客户）
    if participant_ids:
        event_data["partner_ids"] = [(6, 0, participant_ids)]

    # 添加其他可选字段（如果没有商机关联，则使用简单描述）
    if not lead_info:
        if description and description.strip():
            event_data["description"] = f"待办事项：{name}\n\n{description.strip()}"
        else:
            event_data["description"] = f"待办事项：{name}"

    if location and location.strip():
        event_data["location"] = location.strip()

    # 创建日历事件（确保在日历中显示）
    try:
        calendar_event_id = odoo.execute_method("calendar.event", "create", [event_data])
        if isinstance(calendar_event_id, list) and len(calendar_event_id) > 0:
            calendar_event_id = calendar_event_id[0]
    except Exception as e:
        # 即使日历事件创建失败，活动已经创建成功
        pass

    # 返回活动ID（主要的创建结果）
    # 注意：这里返回的是活动ID，但同时也创建了日历事件用于在日历中显示
    return CreateCalendarResponse(success=True, id=activity_id)

class SearchPartnerByNameResponse(BaseModel):
    """Response model for the search_partner_by_name tool."""
    success: bool = Field(description="Indicates if the search was successful")
    result: Optional[List[PartnerSearchResult]] = Field(
        default=None, description="List of partner search results"
    )
    error: Optional[str] = Field(default=None, description="Error message, if any")

@mcp.tool(name="按名称查询公司伙伴", description="根据名称模糊搜索公司类型的伙伴（is_company=True）")
def search_partner_by_name(
    ctx: Context,
    name: str = Field(description="要搜索的伙伴名称或部分名称"),
    limit: int = Field(default=10, description="返回的最大结果数。如果大于等于1，则限制返回指定数量的记录；小于1则查询全部记录"),
) -> SearchPartnerByNameResponse:
    """
    Search for company partners by name (is_company=True, name ilike).

    Parameters:
        name: 伙伴名称或部分名称
        limit: 返回的最大结果数（默认10）。如果大于等于1，则限制返回指定数量；小于1则查询全部

    Returns:
        SearchPartnerByNameResponse containing results or error information.
    """
    odoo = ctx.request_context.lifespan_context.odoo
    model = "res.partner"
    method = "search_read"
    args = [[
        "&",
        ["is_company", "=", True],
        ["name", "ilike", name]
    ]]

    # 如果 limit 大于等于 1，则设置 limit；否则查询全部（不设置 limit）
    kwargs = {"fields": ["name", "comment"]}
    if limit >= 1:
        kwargs["limit"] = limit

    try:
        result = odoo.execute_method(model, method, *args, **kwargs)
        parsed_result = [
            PartnerSearchResult(
                id=item.get("id"),
                name=item.get("name"),
                comment=safe_get_string_field(item, "comment"),
            )
            for item in result
        ]
        return SearchPartnerByNameResponse(success=True, result=parsed_result)
    except Exception as e:
        return SearchPartnerByNameResponse(success=False, error=str(e))

class CreateCustomerResponse(BaseModel):
    """Response model for the create_customer tool."""
    success: bool = Field(description="Indicates if the creation was successful")
    id: Optional[int] = Field(default=None, description="Created customer ID")
    error: Optional[str] = Field(default=None, description="Error message, if any")

@mcp.tool(name="创建客户", description="创建一个新的客户（个人或公司）")
def create_customer(
    ctx: Context,
    name: str = Field(description="客户名称"),
    is_company: bool = Field(default=True, description="是否为公司（True=公司，False=个人）"),
    email: Optional[str] = Field(default=None, description="邮箱地址"),
    phone: Optional[str] = Field(default=None, description="电话号码"),
    mobile: Optional[str] = Field(default=None, description="手机号码"),
    street: Optional[str] = Field(default=None, description="街道地址"),
    city: Optional[str] = Field(default=None, description="城市"),
    country_id: Optional[int] = Field(default=None, description="国家ID（可选）"),
    comment: Optional[str] = Field(default=None, description="备注信息"),
) -> CreateCustomerResponse:
    """
    Create a new customer (individual or company).

    Parameters:
        name: 客户名称
        is_company: 是否为公司（True=公司，False=个人，默认True）
        email: 邮箱地址
        phone: 电话号码
        mobile: 手机号码
        street: 街道地址
        city: 城市
        country_id: 国家ID（可选）
        comment: 备注信息

    Returns:
        CreateCustomerResponse containing the new customer ID or error information.
    """
    odoo = ctx.request_context.lifespan_context.odoo

    # 校验必填字段
    if not name or name.strip() == "":
        return CreateCustomerResponse(success=False, error="客户名称不能为空")

    # 校验邮箱格式（如果提供）
    if email and email.strip():
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email.strip()):
            return CreateCustomerResponse(success=False, error="邮箱格式不正确")

    model = "res.partner"
    method = "create"

    # 构建客户数据
    customer_data = {
        "name": name.strip(),
        "is_company": is_company,
        "customer_rank": 1,  # 标记为客户
        "supplier_rank": 0,  # 不是供应商
    }

    # 添加可选字段
    if email and email.strip():
        customer_data["email"] = email.strip()
    if phone and phone.strip():
        customer_data["phone"] = phone.strip()
    if mobile and mobile.strip():
        customer_data["mobile"] = mobile.strip()
    if street and street.strip():
        customer_data["street"] = street.strip()
    if city and city.strip():
        customer_data["city"] = city.strip()
    if country_id:
        customer_data["country_id"] = country_id
    if comment and comment.strip():
        customer_data["comment"] = comment.strip()

    args = [customer_data]

    try:
        customer_id = odoo.execute_method(model, method, args)
        # Odoo's create method returns a list of IDs, we need the first one
        if isinstance(customer_id, list) and len(customer_id) > 0:
            customer_id = customer_id[0]
        return CreateCustomerResponse(success=True, id=customer_id)
    except Exception as e:
        return CreateCustomerResponse(success=False, error=str(e))

class CreateLeadResponse(BaseModel):
    """Response model for the create_lead tool."""
    success: bool = Field(description="Indicates if the creation was successful")
    id: Optional[int] = Field(default=None, description="Created lead ID")
    error: Optional[str] = Field(default=None, description="Error message, if any")

@mcp.tool(name="创建线索", description="创建一个新的销售商机，可以基于现有客户或手动输入信息")
def create_lead(
    ctx: Context,
    name: str = Field(description="商机名称/机会名称"),
    partner_id: Optional[int] = Field(default=None, description="客户ID（如果基于现有客户创建）"),
    contact_name: Optional[str] = Field(default=None, description="联系人姓名"),
    email_from: Optional[str] = Field(default=None, description="邮箱地址"),
    phone: Optional[str] = Field(default=None, description="电话号码"),
    mobile: Optional[str] = Field(default=None, description="手机号码"),
    company_name: Optional[str] = Field(default=None, description="公司名称"),
    street: Optional[str] = Field(default=None, description="街道地址"),
    city: Optional[str] = Field(default=None, description="城市"),
    country_id: Optional[int] = Field(default=None, description="国家ID（可选）"),
    expected_revenue: Optional[float] = Field(default=None, description="预期收入"),
    probability: Optional[float] = Field(default=10.0, description="成功概率（0-100，默认10）"),
    description: Optional[str] = Field(default=None, description="商机描述"),
    source_id: Optional[int] = Field(default=None, description="来源ID（可选）"),
) -> CreateLeadResponse:
    """
    Create a new sales opportunity, either based on existing customer or with manual input.

    Parameters:
        name: 商机名称/机会名称
        partner_id: 客户ID（如果基于现有客户创建）
        contact_name: 联系人姓名
        email_from: 邮箱地址
        phone: 电话号码
        mobile: 手机号码
        company_name: 公司名称
        street: 街道地址
        city: 城市
        country_id: 国家ID（可选）
        expected_revenue: 预期收入
        probability: 成功概率（0-100，默认10）
        description: 商机描述
        source_id: 来源ID（可选）

    Returns:
        CreateLeadResponse containing the new opportunity ID or error information.
    """
    odoo = ctx.request_context.lifespan_context.odoo

    # 校验必填字段
    if not name or name.strip() == "":
        return CreateLeadResponse(success=False, error="商机名称不能为空")

    # 校验邮箱格式（如果提供）
    if email_from and email_from.strip():
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email_from.strip()):
            return CreateLeadResponse(success=False, error="邮箱格式不正确")

    # 校验概率范围
    if probability is not None and (probability < 0 or probability > 100):
        return CreateLeadResponse(success=False, error="成功概率必须在0-100之间")

    # 校验预期收入
    if expected_revenue is not None and expected_revenue < 0:
        return CreateLeadResponse(success=False, error="预期收入不能为负数")

    # 如果提供了客户ID，先获取客户信息
    partner_info = None
    if partner_id:
        try:
            partner_result = odoo.execute_method(
                "res.partner",
                "read",
                [partner_id],
                ["name", "email", "phone", "mobile", "street", "city", "country_id", "is_company"]
            )
            if partner_result:
                partner_info = partner_result[0]
            else:
                return CreateLeadResponse(success=False, error=f"找不到ID为{partner_id}的客户")
        except Exception as e:
            return CreateLeadResponse(success=False, error=f"获取客户信息失败: {str(e)}")

    model = "crm.lead"
    method = "create"

    # 构建线索数据
    lead_data = {
        "name": name.strip(),
        "type": "opportunity",  # 直接标记为商机类型
    }

    # 如果基于现有客户创建，使用客户信息
    if partner_info:
        lead_data["partner_id"] = partner_id
        # 使用客户信息作为默认值，但允许手动输入的参数覆盖
        if not contact_name and partner_info.get("name"):
            lead_data["contact_name"] = partner_info["name"]
        if not email_from and partner_info.get("email"):
            lead_data["email_from"] = partner_info["email"]
        if not phone and partner_info.get("phone"):
            lead_data["phone"] = partner_info["phone"]
        if not mobile and partner_info.get("mobile"):
            lead_data["mobile"] = partner_info["mobile"]
        if not street and partner_info.get("street"):
            lead_data["street"] = partner_info["street"]
        if not city and partner_info.get("city"):
            lead_data["city"] = partner_info["city"]
        if not country_id and partner_info.get("country_id"):
            # country_id 在 Odoo 中是 [id, name] 格式
            if isinstance(partner_info["country_id"], list):
                lead_data["country_id"] = partner_info["country_id"][0]
            else:
                lead_data["country_id"] = partner_info["country_id"]
        # 如果客户是公司，使用公司名称
        if partner_info.get("is_company") and not company_name:
            lead_data["partner_name"] = partner_info["name"]

    # 添加手动输入的字段（这些会覆盖从客户信息获取的默认值）
    if contact_name and contact_name.strip():
        lead_data["contact_name"] = contact_name.strip()
    if email_from and email_from.strip():
        lead_data["email_from"] = email_from.strip()
    if phone and phone.strip():
        lead_data["phone"] = phone.strip()
    if mobile and mobile.strip():
        lead_data["mobile"] = mobile.strip()
    if company_name and company_name.strip():
        lead_data["partner_name"] = company_name.strip()
    if street and street.strip():
        lead_data["street"] = street.strip()
    if city and city.strip():
        lead_data["city"] = city.strip()
    if country_id:
        lead_data["country_id"] = country_id
    if expected_revenue is not None:
        lead_data["expected_revenue"] = expected_revenue
    if probability is not None:
        lead_data["probability"] = probability
    if description and description.strip():
        lead_data["description"] = description.strip()
    if source_id:
        lead_data["source_id"] = source_id

    args = [lead_data]

    try:
        lead_id = odoo.execute_method(model, method, args)
        # Odoo's create method returns a list of IDs, we need the first one
        if isinstance(lead_id, list) and len(lead_id) > 0:
            lead_id = lead_id[0]
        return CreateLeadResponse(success=True, id=lead_id)
    except Exception as e:
        return CreateLeadResponse(success=False, error=str(e))
@mcp.tool(name="get-current-date", description="获取当前日期，以上海时区（Asia/Shanghai, UTC+8）为准，返回格式为 \"yyyy-MM-dd HH:mm:ss\",为其他需要日期的接口提供准确的日期输入。")
def get_current_date() -> str:
    """
    获取当前日期，以上海时区（Asia/Shanghai, UTC+8）为准，返回格式为 "yyyy-MM-dd HH:mm:ss"
    """
    return datetime.now(tz=ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
