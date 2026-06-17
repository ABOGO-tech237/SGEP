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
	ReportJobStatusResponseSerializer,
	TokenResponseSerializer,
)
from classes.serializers import ClassSerializer, SubjectSerializer
from classes.views import ClassDetailView, ClassListCreateView, SubjectDetailView, SubjectListCreateView
from core.serializers import AcademicYearSerializer, AdminDashboardResponseSerializer, SchoolSerializer
from core.views import (
	AcademicYearDetailView,
	AcademicYearListCreateView,
	AdminDashboardView,
	SchoolDetailView,
	SchoolListCreateView,
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
	GradeResultsExportView,
	ReportCardDownloadView,
	ReportCardGenerateView,
	ReportCardPublishView,
	ReportCardStatusView,
)
from parents.serializers import ParentMessageSerializer
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
from reports.views import ReportJobDownloadView, ReportJobStatusView

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

extend_schema_view(
	get=extend_schema(
		tags=["Grades"],
		summary="Exporter les résultats en Excel",
		parameters=[
			OpenApiParameter("class_id", str, OpenApiParameter.QUERY, required=True),
			OpenApiParameter("period_id", str, OpenApiParameter.QUERY, required=True),
		],
		responses={202: JobIdResponseSerializer},
	),
)(GradeResultsExportView)

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
		responses={200: ParentMessageSerializer(many=True)},
	),
	post=extend_schema(
		tags=["Parent Portal"],
		summary="Messagerie — envoyer",
		request=ParentMessageCreateSerializer,
		responses={201: ParentMessageSerializer},
	),
)(ParentMessagesView)

# --- Core (schools & academic years) ---

extend_schema_view(
	get=extend_schema(tags=["Core"], summary="Lister les écoles", responses={200: SchoolSerializer(many=True)}),
	post=extend_schema(
		tags=["Core"],
		summary="Créer une école",
		request=SchoolSerializer,
		responses={201: SchoolSerializer},
	),
)(SchoolListCreateView)

extend_schema_view(
	get=extend_schema(tags=["Core"], summary="Détail école", responses={200: SchoolSerializer}),
	patch=extend_schema(
		tags=["Core"],
		summary="Modifier une école",
		request=SchoolSerializer,
		responses={200: SchoolSerializer},
	),
)(SchoolDetailView)

extend_schema_view(
	get=extend_schema(
		tags=["Core"],
		summary="Lister les années scolaires",
		parameters=[OpenApiParameter("school_id", str, OpenApiParameter.QUERY)],
		responses={200: AcademicYearSerializer(many=True)},
	),
	post=extend_schema(
		tags=["Core"],
		summary="Créer une année scolaire",
		request=AcademicYearSerializer,
		responses={201: AcademicYearSerializer},
	),
)(AcademicYearListCreateView)

extend_schema_view(
	get=extend_schema(tags=["Core"], summary="Détail année scolaire", responses={200: AcademicYearSerializer}),
	patch=extend_schema(
		tags=["Core"],
		summary="Modifier une année scolaire",
		request=AcademicYearSerializer,
		responses={200: AcademicYearSerializer},
	),
)(AcademicYearDetailView)

# --- Classes & subjects ---

extend_schema_view(
	get=extend_schema(
		tags=["Classes"],
		summary="Lister les classes",
		parameters=[
			OpenApiParameter("academic_year_id", str, OpenApiParameter.QUERY),
			OpenApiParameter("level_id", str, OpenApiParameter.QUERY),
		],
		responses={200: ClassSerializer(many=True)},
	),
	post=extend_schema(
		tags=["Classes"],
		summary="Créer une classe",
		request=ClassSerializer,
		responses={201: ClassSerializer},
	),
)(ClassListCreateView)

extend_schema_view(
	get=extend_schema(tags=["Classes"], summary="Détail classe", responses={200: ClassSerializer}),
	patch=extend_schema(
		tags=["Classes"],
		summary="Modifier une classe",
		request=ClassSerializer,
		responses={200: ClassSerializer},
	),
)(ClassDetailView)

extend_schema_view(
	get=extend_schema(
		tags=["Classes"],
		summary="Lister les matières",
		parameters=[OpenApiParameter("class_id", str, OpenApiParameter.QUERY)],
		responses={200: SubjectSerializer(many=True)},
	),
	post=extend_schema(
		tags=["Classes"],
		summary="Créer une matière",
		request=SubjectSerializer,
		responses={201: SubjectSerializer},
	),
)(SubjectListCreateView)

extend_schema_view(
	get=extend_schema(tags=["Classes"], summary="Détail matière", responses={200: SubjectSerializer}),
	patch=extend_schema(
		tags=["Classes"],
		summary="Modifier une matière",
		request=SubjectSerializer,
		responses={200: SubjectSerializer},
	),
)(SubjectDetailView)

# --- Report jobs ---

extend_schema_view(
	get=extend_schema(
		tags=["Reports"],
		summary="Statut d'un export asynchrone",
		responses={200: ReportJobStatusResponseSerializer},
	),
)(ReportJobStatusView)

extend_schema_view(
	get=extend_schema(
		tags=["Reports"],
		summary="Télécharger un export asynchrone",
		responses={(200, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"): OpenApiResponse(description="Fichier Excel ou PDF")},
	),
)(ReportJobDownloadView)

# --- Admin dashboard ---

extend_schema_view(
	get=extend_schema(
		tags=["Admin"],
		summary="Tableau de bord administrateur",
		description="Statistiques élèves, classes, finance et activité récente depuis Appwrite.",
		responses={200: AdminDashboardResponseSerializer},
	),
)(AdminDashboardView)
