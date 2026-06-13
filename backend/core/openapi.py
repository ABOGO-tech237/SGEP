"""
Enregistre les annotations OpenAPI (drf-spectacular) sur les vues DRF.
Importé depuis config/urls.py au démarrage des routes.
"""

from __future__ import annotations

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object

from accounts.authentication import AppwriteJWTAuthentication


class AppwriteJWTAuthenticationScheme(OpenApiAuthenticationExtension):
	target_class = AppwriteJWTAuthentication
	name = "bearerAuth"

	def get_security_definition(self, auto_schema):
		return build_bearer_security_scheme_object(
			header_name="Authorization",
			token_prefix="Bearer",
			bearer_format="JWT",
		)


from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view

from accounts.serializers import ChangePasswordSerializer, LoginSerializer, LogoutSerializer, RefreshSerializer
from accounts.views import ChangePasswordView, LoginView, LogoutView, RefreshTokenView
from attendance.serializers import (
	AttendanceCreateSerializer,
	AttendanceSerializer,
	AttendanceStatsSerializer,
	AttendanceUpdateSerializer,
	JustifySerializer,
)
from attendance.views import (
	AttendanceDetailView,
	AttendanceExportView,
	AttendanceJustifyView,
	AttendanceListCreateView,
	AttendanceStatsView,
)
from core.openapi_serializers import (
	AccessTokenResponseSerializer,
	FinanceDashboardResponseSerializer,
	InvoiceGenerateResponseSerializer,
	JobIdResponseSerializer,
	MessageResponseSerializer,
	ParentProfileResponseSerializer,
	ParentMessageCreateSerializer,
	ReportCardStatusResponseSerializer,
	TokenResponseSerializer,
)
from finance.serializers import InvoiceGenerateSerializer, InvoiceSerializer, PaymentCreateSerializer, PaymentSerializer
from finance.views import (
	FinanceDashboardView,
	FinanceExportExcelView,
	FinanceInvoiceGenerateView,
	FinanceInvoiceListView,
	FinanceOverdueView,
	FinancePaymentCreateView,
	FinancePaymentReceiptView,
)
from grades.serializers import (
	BulkGradeCreateSerializer,
	GradeCreateSerializer,
	GradeSerializer,
	ReportCardGenerateSerializer,
	ReportCardSerializer,
)
from grades.views import (
	GradeBulkCreateView,
	GradeDetailView,
	GradeListCreateView,
	ReportCardDownloadView,
	ReportCardGenerateView,
	ReportCardPublishView,
	ReportCardStatusView,
)
from parents.views import (
	ParentAttendanceView,
	ParentGradesView,
	ParentInvoiceReceiptView,
	ParentInvoicesView,
	ParentMeView,
	ParentMessagesView,
	ParentReportCardDownloadView,
	ParentReportCardsView,
	ParentStudentView,
)
from students.serializers import (
	StudentCreateSerializer,
	StudentEnrollSerializer,
	StudentListSerializer,
	StudentPromoteSerializer,
	StudentSerializer,
)
from students.views import (
	StudentDetailView,
	StudentEnrollView,
	StudentExportExcelView,
	StudentExportPDFView,
	StudentHistoryView,
	StudentListCreateView,
	StudentPromoteView,
)

# --- Auth ---

extend_schema_view(
	post=extend_schema(
		tags=["Auth"],
		summary="Connexion",
		description="Authentifie un utilisateur et retourne les tokens JWT.",
		request=LoginSerializer,
		responses={200: TokenResponseSerializer},
		auth=[],
	),
)(LoginView)

extend_schema_view(
	post=extend_schema(
		tags=["Auth"],
		summary="Renouveler le token d'accès",
		request=RefreshSerializer,
		responses={200: AccessTokenResponseSerializer},
		auth=[],
	),
)(RefreshTokenView)

extend_schema_view(
	post=extend_schema(
		tags=["Auth"],
		summary="Déconnexion",
		description="Blackliste le refresh token.",
		request=LogoutSerializer,
		responses={204: None},
	),
)(LogoutView)

extend_schema_view(
	post=extend_schema(
		tags=["Auth"],
		summary="Changer le mot de passe",
		request=ChangePasswordSerializer,
		responses={200: MessageResponseSerializer},
	),
)(ChangePasswordView)

# --- Students ---

extend_schema_view(
	get=extend_schema(
		tags=["Students"],
		summary="Lister les élèves",
		parameters=[
			OpenApiParameter("class_id", str, OpenApiParameter.QUERY),
			OpenApiParameter("academic_year_id", str, OpenApiParameter.QUERY),
			OpenApiParameter("is_active", bool, OpenApiParameter.QUERY),
			OpenApiParameter("search", str, OpenApiParameter.QUERY),
			OpenApiParameter("page", int, OpenApiParameter.QUERY),
			OpenApiParameter("page_size", int, OpenApiParameter.QUERY),
		],
		responses={200: StudentListSerializer(many=True)},
	),
	post=extend_schema(
		tags=["Students"],
		summary="Créer un élève",
		request=StudentCreateSerializer,
		responses={201: StudentSerializer},
	),
)(StudentListCreateView)

extend_schema_view(
	get=extend_schema(tags=["Students"], summary="Détail élève", responses={200: StudentSerializer}),
	patch=extend_schema(
		tags=["Students"],
		summary="Modifier un élève",
		request=StudentCreateSerializer,
		responses={200: StudentSerializer},
	),
	delete=extend_schema(tags=["Students"], summary="Supprimer un élève (soft delete)", responses={204: None}),
)(StudentDetailView)

extend_schema_view(
	get=extend_schema(
		tags=["Students"],
		summary="Historique élève",
		responses={200: OpenApiResponse(description="Historique des événements de l'élève")},
	),
)(StudentHistoryView)

extend_schema_view(
	post=extend_schema(
		tags=["Students"],
		summary="Inscrire un élève",
		request=StudentEnrollSerializer,
		responses={200: StudentSerializer},
	),
)(StudentEnrollView)

extend_schema_view(
	post=extend_schema(
		tags=["Students"],
		summary="Promouvoir un élève",
		request=StudentPromoteSerializer,
		responses={200: StudentSerializer},
	),
)(StudentPromoteView)

extend_schema_view(
	get=extend_schema(tags=["Students"], summary="Exporter les élèves en PDF", responses={202: JobIdResponseSerializer}),
)(StudentExportPDFView)

extend_schema_view(
	get=extend_schema(tags=["Students"], summary="Exporter les élèves en Excel", responses={202: JobIdResponseSerializer}),
)(StudentExportExcelView)

# --- Attendance ---

extend_schema_view(
	get=extend_schema(
		tags=["Attendance"],
		summary="Lister les absences",
		parameters=[
			OpenApiParameter("class_id", str, OpenApiParameter.QUERY),
			OpenApiParameter("student_id", str, OpenApiParameter.QUERY),
			OpenApiParameter("date_from", str, OpenApiParameter.QUERY, description="ISO datetime"),
			OpenApiParameter("date_to", str, OpenApiParameter.QUERY, description="ISO datetime"),
		],
		responses={200: AttendanceSerializer(many=True)},
	),
	post=extend_schema(
		tags=["Attendance"],
		summary="Enregistrer une absence ou un retard",
		request=AttendanceCreateSerializer,
		responses={201: AttendanceSerializer},
	),
)(AttendanceListCreateView)

extend_schema_view(
	put=extend_schema(
		tags=["Attendance"],
		summary="Modifier un enregistrement de présence",
		request=AttendanceUpdateSerializer,
		responses={200: AttendanceSerializer},
	),
)(AttendanceDetailView)

extend_schema_view(
	post=extend_schema(
		tags=["Attendance"],
		summary="Justifier une absence",
		request=JustifySerializer,
		responses={200: AttendanceSerializer},
	),
)(AttendanceJustifyView)

extend_schema_view(
	get=extend_schema(
		tags=["Attendance"],
		summary="Statistiques d'absentéisme par classe",
		parameters=[
			OpenApiParameter("class_id", str, OpenApiParameter.QUERY, required=True),
			OpenApiParameter("date_from", str, OpenApiParameter.QUERY, required=True),
			OpenApiParameter("date_to", str, OpenApiParameter.QUERY, required=True),
		],
		responses={200: AttendanceStatsSerializer(many=True)},
	),
)(AttendanceStatsView)

extend_schema_view(
	get=extend_schema(
		tags=["Attendance"],
		summary="Exporter les absences",
		parameters=[OpenApiParameter("format", str, OpenApiParameter.QUERY, description="pdf ou excel")],
		responses={202: JobIdResponseSerializer},
	),
)(AttendanceExportView)

# --- Grades ---

extend_schema_view(
	get=extend_schema(
		tags=["Grades"],
		summary="Lister les notes",
		parameters=[
			OpenApiParameter("class_id", str, OpenApiParameter.QUERY),
			OpenApiParameter("subject_id", str, OpenApiParameter.QUERY),
			OpenApiParameter("period_id", str, OpenApiParameter.QUERY, description="Séquence / période"),
		],
		responses={200: GradeSerializer(many=True)},
	),
	post=extend_schema(
		tags=["Grades"],
		summary="Créer une note",
		request=GradeCreateSerializer,
		responses={201: GradeSerializer},
	),
)(GradeListCreateView)

extend_schema_view(
	put=extend_schema(
		tags=["Grades"],
		summary="Modifier une note",
		request=GradeCreateSerializer,
		responses={200: GradeSerializer},
	),
)(GradeDetailView)

extend_schema_view(
	post=extend_schema(
		tags=["Grades"],
		summary="Saisie en masse des notes",
		request=BulkGradeCreateSerializer,
		responses={201: GradeSerializer(many=True)},
	),
)(GradeBulkCreateView)

# --- Report cards ---

extend_schema_view(
	post=extend_schema(
		tags=["Report Cards"],
		summary="Générer les bulletins d'une classe",
		request=ReportCardGenerateSerializer,
		responses={202: JobIdResponseSerializer},
	),
)(ReportCardGenerateView)

extend_schema_view(
	get=extend_schema(
		tags=["Report Cards"],
		summary="Statut de génération des bulletins",
		responses={200: ReportCardStatusResponseSerializer},
	),
)(ReportCardStatusView)

extend_schema_view(
	get=extend_schema(
		tags=["Report Cards"],
		summary="Télécharger un bulletin PDF",
		responses={(200, "application/pdf"): OpenApiResponse(description="Fichier PDF")},
	),
)(ReportCardDownloadView)

extend_schema_view(
	post=extend_schema(
		tags=["Report Cards"],
		summary="Publier un bulletin",
		description="Passe le bulletin en statut published et notifie le parent.",
		request=None,
		responses={200: ReportCardSerializer},
	),
)(ReportCardPublishView)

# --- Finance ---

extend_schema_view(
	get=extend_schema(
		tags=["Finance"],
		summary="Lister les factures",
		parameters=[
			OpenApiParameter("student_id", str, OpenApiParameter.QUERY),
			OpenApiParameter("status", str, OpenApiParameter.QUERY),
		],
		responses={200: InvoiceSerializer(many=True)},
	),
)(FinanceInvoiceListView)

extend_schema_view(
	post=extend_schema(
		tags=["Finance"],
		summary="Générer des factures",
		description="Génère des factures pour une classe ou toute l'école.",
		request=InvoiceGenerateSerializer,
		responses={201: InvoiceGenerateResponseSerializer},
	),
)(FinanceInvoiceGenerateView)

extend_schema_view(
	post=extend_schema(
		tags=["Finance"],
		summary="Enregistrer un paiement",
		request=PaymentCreateSerializer,
		responses={201: PaymentSerializer},
	),
)(FinancePaymentCreateView)

extend_schema_view(
	get=extend_schema(
		tags=["Finance"],
		summary="Télécharger le reçu de paiement",
		responses={(200, "application/pdf"): OpenApiResponse(description="Reçu PDF ou HTML")},
	),
)(FinancePaymentReceiptView)

extend_schema_view(
	get=extend_schema(tags=["Finance"], summary="Factures en retard", responses={200: InvoiceSerializer(many=True)}),
)(FinanceOverdueView)

extend_schema_view(
	get=extend_schema(
		tags=["Finance"],
		summary="Tableau de bord finance",
		responses={200: FinanceDashboardResponseSerializer},
	),
)(FinanceDashboardView)

extend_schema_view(
	get=extend_schema(tags=["Finance"], summary="Exporter la finance en Excel", responses={202: JobIdResponseSerializer}),
)(FinanceExportExcelView)

# --- Parent portal ---

extend_schema_view(
	get=extend_schema(
		tags=["Parent Portal"],
		summary="Profil parent",
		responses={200: ParentProfileResponseSerializer},
	),
)(ParentMeView)

extend_schema_view(
	get=extend_schema(tags=["Parent Portal"], summary="Informations de l'élève lié", responses={200: StudentSerializer}),
)(ParentStudentView)

extend_schema_view(
	get=extend_schema(
		tags=["Parent Portal"],
		summary="Notes de l'élève",
		parameters=[OpenApiParameter("period_id", str, OpenApiParameter.QUERY)],
		responses={200: GradeSerializer(many=True)},
	),
)(ParentGradesView)

extend_schema_view(
	get=extend_schema(
		tags=["Parent Portal"],
		summary="Absences de l'élève",
		responses={200: AttendanceSerializer(many=True)},
	),
)(ParentAttendanceView)

extend_schema_view(
	get=extend_schema(
		tags=["Parent Portal"],
		summary="Bulletins de l'élève",
		responses={200: ReportCardSerializer(many=True)},
	),
)(ParentReportCardsView)

extend_schema_view(
	get=extend_schema(
		tags=["Parent Portal"],
		summary="Télécharger un bulletin (parent)",
		responses={(200, "application/pdf"): OpenApiResponse(description="Fichier PDF")},
	),
)(ParentReportCardDownloadView)

extend_schema_view(
	get=extend_schema(
		tags=["Parent Portal"],
		summary="Factures de l'élève",
		responses={200: InvoiceSerializer(many=True)},
	),
)(ParentInvoicesView)

extend_schema_view(
	get=extend_schema(
		tags=["Parent Portal"],
		summary="Reçu de paiement (parent)",
		responses={(200, "application/pdf"): OpenApiResponse(description="Reçu PDF ou HTML")},
	),
)(ParentInvoiceReceiptView)

extend_schema_view(
	get=extend_schema(
		tags=["Parent Portal"],
		summary="Messagerie — liste",
		responses={200: OpenApiResponse(description="Liste des messages")},
	),
	post=extend_schema(
		tags=["Parent Portal"],
		summary="Messagerie — envoyer",
		request=ParentMessageCreateSerializer,
		responses={201: MessageResponseSerializer},
	),
)(ParentMessagesView)
