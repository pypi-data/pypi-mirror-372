from ai_app.utils import PydanticForbidExtra


class AppConfig(PydanticForbidExtra):
    show: bool = False


class JiraServiceDesk(AppConfig):
    jira_requests_spreadsheet_id: str | None = None
    n_closest_requests: int = 5
    service_desks: list[int] | None = None


class JiraManualTests(AppConfig): ...


class SoftwareRequirementsSpecification(AppConfig): ...


class VoiceAssistant(AppConfig): ...


class GovernanceAgent(AppConfig): ...


class MergeRequestReview(AppConfig): ...


class SqlAgent(AppConfig): ...


class PresentationReview(AppConfig): ...


class Apps(PydanticForbidExtra):
    jira_service_desk: JiraServiceDesk = JiraServiceDesk()
    jira_manual_tests: JiraManualTests = JiraManualTests()
    software_requirements_specification: SoftwareRequirementsSpecification = (
        SoftwareRequirementsSpecification()
    )
    voice_assistant: VoiceAssistant = VoiceAssistant()
    merge_request_review: MergeRequestReview = MergeRequestReview()
    sql_agent: SqlAgent = SqlAgent()
    presentation_review: PresentationReview = PresentationReview()
    governance_agent: GovernanceAgent = GovernanceAgent()
