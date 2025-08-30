from enum import Enum
from typing import Optional, List, Any
from datetime import datetime


class Kind(Enum):
    PEDAGOGY = "pedagogy"
    PROJECT = "project"
    SCOLARITY = "scolarity"


class Tier(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    NONE = "none"

class Achievement:
    id: int
    name: str
    description: str
    tier: Tier
    kind: Kind
    visible: bool
    image: str
    nbr_of_success: Optional[int]
    users_url: str

    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        tier: Tier,
        kind: Kind,
        visible: bool,
        image: str,
        nbr_of_success: Optional[int],
        users_url: str,
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.tier = tier
        self.kind = kind
        self.visible = visible
        self.image = image
        self.nbr_of_success = nbr_of_success
        self.users_url = users_url

    @staticmethod
    def empty():
        return Achievement(None, None, None, None, None, None, None, None, None)

    @staticmethod
    def from_dict(o: dict):
        out = Achievement.empty()
        out.id = o.get("id")
        out.name = o.get("name")
        out.description = o.get("description")
        out.tier = o.get("tier")
        out.kind = o.get("kind")
        out.visible = o.get("visible")
        out.image = o.get("image")
        out.nbr_of_success = o.get("nbr_of_success")
        out.users_url = o.get("users_url")
        return out


class Language:
    id: int
    name: str
    identifier: str
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        id: int,
        name: str,
        identifier: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.id = id
        self.name = name
        self.identifier = identifier
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def empty():
        return Language(None, None, None, None, None)

    @staticmethod
    def from_dict(o: dict):
        out = Language.empty()
        out.id = o.get("id")
        out.name = o.get("name")
        out.identifier = o.get("identifier")
        out.created_at = o.get("created_at")
        out.updated_at = o.get("updated_at")
        return out


class Campus:
    id: int
    name: str
    time_zone: str
    language: Language
    users_count: int
    vogsphere_id: int
    country: str
    address: str
    zip: int
    city: str
    website: str
    facebook: str
    twitter: str
    active: bool
    public: bool
    email_extension: str
    default_hidden_phone: bool

    def __init__(
        self,
        _id: int,
        name: str,
        time_zone: str,
        language: Language,
        users_count: int,
        vogsphere_id: int,
        country: str,
        address: str,
        _zip: int,
        city: str,
        website: str,
        facebook: str,
        twitter: str,
        active: bool,
        public: bool,
        email_extension: str,
        default_hidden_phone: bool,
    ) -> None:
        self.id = _id
        self.name = name
        self.time_zone = time_zone
        self.language = language
        self.users_count = users_count
        self.vogsphere_id = vogsphere_id
        self.country = country
        self.address = address
        self.zip = _zip
        self.city = city
        self.website = website
        self.facebook = facebook
        self.twitter = twitter
        self.active = active
        self.public = public
        self.email_extension = email_extension
        self.default_hidden_phone = default_hidden_phone

    @staticmethod
    def empty():
        return Campus(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    @staticmethod
    def from_dict(o: dict):
        out = Campus.empty()
        out.id = o.get("id")
        out.name = o.get("name")
        out.time_zone = o.get("time_zone")
        out.language = o.get("language")
        out.users_count = o.get("users_count")
        out.vogsphere_id = o.get("vogsphere_id")
        out.country = o.get("country")
        out.address = o.get("address")
        out._zip = o.get("zip")
        out.city = o.get("city")
        out.website = o.get("website")
        out.facebook = o.get("facebook")
        out.twitter = o.get("twitter")
        out.active = o.get("active")
        out.public = o.get("public")
        out.email_extension = o.get("email_extension")
        out.default_hidden_phone = o.get("default_hidden_phone")
        return out


class CampusUser:
    id: int
    user_id: int
    campus_id: int
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        _id: int,
        user_id: int,
        campus_id: int,
        is_primary: bool,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.id = _id
        self.user_id = user_id
        self.campus_id = campus_id
        self.is_primary = is_primary
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def empty():
        return CampusUser(None, None, None, None, None, None)

    @staticmethod
    def from_dict(o: dict):
        out = CampusUser.empty()
        out.id = o.get("id")
        out.user_id = o.get("user_id")
        out.campus_id = o.get("campus_id")
        out.is_primary = o.get("is_primary")
        out.created_at = o.get("created_at")
        out.updated_at = o.get("updated_at")
        return out


class Cursus:
    id: int
    created_at: datetime
    name: str
    slug: str
    kind: str

    def __init__(
        self, _id: int, created_at: datetime, name: str, slug: str, kind: str
    ) -> None:
        self.id = _id
        self.created_at = created_at
        self.name = name
        self.slug = slug
        self.kind = kind

    @staticmethod
    def empty():
        return Cursus(None, None, None, None, None)

    @staticmethod
    def from_dict(o: dict):
        out = Cursus.empty()
        out.id = o.get("id")
        out.created_at = o.get("created_at")
        out.name = o.get("name")
        out.slug = o.get("slug")
        out.kind = o.get("kind")
        return out


class Skill:
    id: int
    name: str
    level: float

    def __init__(self, _id: int, name: str, level: float) -> None:
        self.id = _id
        self.name = name
        self.level = level

    @staticmethod
    def empty():
        return Skill(None, None, None)

    @staticmethod
    def from_dict(o: dict):
        out = Skill.empty()
        out.id = o.get("id")
        out.name = o.get("name")
        out.level = o.get("level")
        return out


class Versions:
    large: str
    medium: str
    small: str
    micro: str

    def __init__(self, large: str, medium: str, small: str, micro: str) -> None:
        self.large = large
        self.medium = medium
        self.small = small
        self.micro = micro

    @staticmethod
    def empty():
        return Versions(None, None, None, None)

    @staticmethod
    def from_dict(o: dict):
        out = Versions.empty()
        out.large = o.get("large")
        out.medium = o.get("medium")
        out.small = o.get("small")
        out.micro = o.get("micro")
        return out


class Image:
    link: str
    versions: Versions

    def __init__(self, link: str, versions: Versions) -> None:
        self.link = link
        self.versions = versions

    @staticmethod
    def empty():
        return Image(None, None)

    @staticmethod
    def from_dict(o: dict):
        out = Image.empty()
        if o is None:
            return out
        out.link = o.get("link")
        out.versions = Versions.from_dict(o.get("versions"))
        return out


class RefUser:
    id: int
    email: str
    login: str
    first_name: str
    last_name: str
    usual_full_name: str
    usual_first_name: None
    url: str
    phone: str
    displayname: str
    kind: str
    image: Image
    staff: bool
    correction_point: int
    pool_month: str
    pool_year: int
    location: str
    wallet: int
    anonymize_date: datetime
    data_erasure_date: datetime
    created_at: datetime
    updated_at: datetime
    alumnized_at: None
    alumni: bool
    active: bool

    def __init__(
        self,
        _id: int,
        email: str,
        login: str,
        first_name: str,
        last_name: str,
        usual_full_name: str,
        usual_first_name: None,
        url: str,
        phone: str,
        displayname: str,
        kind: str,
        image: Image,
        staff: bool,
        correction_point: int,
        pool_month: str,
        pool_year: int,
        location: str,
        wallet: int,
        anonymize_date: datetime,
        data_erasure_date: datetime,
        created_at: datetime,
        updated_at: datetime,
        alumnized_at: None,
        alumni: bool,
        active: bool,
    ) -> None:
        self.id = _id
        self.email = email
        self.login = login
        self.first_name = first_name
        self.last_name = last_name
        self.usual_full_name = usual_full_name
        self.usual_first_name = usual_first_name
        self.url = url
        self.phone = phone
        self.displayname = displayname
        self.kind = kind
        self.image = image
        self.staff = staff
        self.correction_point = correction_point
        self.pool_month = pool_month
        self.pool_year = pool_year
        self.location = location
        self.wallet = wallet
        self.anonymize_date = anonymize_date
        self.data_erasure_date = data_erasure_date
        self.created_at = created_at
        self.updated_at = updated_at
        self.alumnized_at = alumnized_at
        self.alumni = alumni
        self.active = active

    @staticmethod
    def empty():
        return RefUser(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    @staticmethod
    def from_dict(o: dict):
        out = RefUser.empty()
        out.id = o.get("id")
        out.email = o.get("email")
        out.login = o.get("login")
        out.first_name = o.get("first_name")
        out.last_name = o.get("last_name")
        out.usual_full_name = o.get("usual_full_name")
        out.usual_first_name = o.get("usual_first_name")
        out.url = o.get("url")
        out.phone = o.get("phone")
        out.displayname = o.get("displayname")
        out.kind = o.get("kind")
        out.image = o.get("image")
        out.staff = o.get("staff")
        out.correction_point = o.get("correction_point")
        out.pool_month = o.get("pool_month")
        out.pool_year = o.get("pool_year")
        out.location = o.get("location")
        out.wallet = o.get("wallet")
        out.anonymize_date = o.get("anonymize_date")
        out.data_erasure_date = o.get("data_erasure_date")
        out.created_at = o.get("created_at")
        out.updated_at = o.get("updated_at")
        out.alumnized_at = o.get("alumnized_at")
        out.alumni = o.get("alumni")
        out.active = o.get("active")
        return out


class CursusUser:
    id: int
    begin_at: datetime
    end_at: Optional[datetime]
    grade: Optional[str]
    level: float
    skills: List[Skill]
    cursus_id: int
    has_coalition: bool
    blackholed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    user: RefUser
    cursus: Cursus

    def __init__(
        self,
        _id: int,
        begin_at: datetime,
        end_at: Optional[datetime],
        grade: Optional[str],
        level: float,
        skills: List[Skill],
        cursus_id: int,
        has_coalition: bool,
        blackholed_at: Optional[datetime],
        created_at: datetime,
        updated_at: datetime,
        user: RefUser,
        cursus: Cursus,
    ) -> None:
        self.id = _id
        self.begin_at = begin_at
        self.end_at = end_at
        self.grade = grade
        self.level = level
        self.skills = skills
        self.cursus_id = cursus_id
        self.has_coalition = has_coalition
        self.blackholed_at = blackholed_at
        self.created_at = created_at
        self.updated_at = updated_at
        self.user = user
        self.cursus = cursus

    @staticmethod
    def empty():
        return CursusUser(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    @staticmethod
    def from_dict(o: dict):
        out = CursusUser.empty()
        out.id = o.get("id")
        out.begin_at = o.get("begin_at")
        out.end_at = o.get("end_at")
        out.grade = o.get("grade")
        out.level = o.get("level")
        out.skills = o.get("skills")
        out.cursus_id = o.get("cursus_id")
        out.has_coalition = o.get("has_coalition")
        out.blackholed_at = o.get("blackholed_at")
        out.created_at = o.get("created_at")
        out.updated_at = o.get("updated_at")
        out.user = RefUser.from_dict(o.get("user"))
        out.cursus = Cursus.from_dict(o.get("cursus"))
        return out


class LanguagesUser:
    id: int
    language_id: int
    user_id: int
    position: int
    created_at: datetime

    def __init__(
        self,
        _id: int,
        language_id: int,
        user_id: int,
        position: int,
        created_at: datetime,
    ) -> None:
        self.id = _id
        self.language_id = language_id
        self.user_id = user_id
        self.position = position
        self.created_at = created_at

    @staticmethod
    def empty():
        return LanguagesUser(
            None,
            None,
            None,
            None,
            None,
        )

    @staticmethod
    def from_dict(o: dict):
        out = LanguagesUser.empty()
        out.id = o.get("id")
        out.language_id = o.get("language_id")
        out.user_id = o.get("user_id")
        out.position = o.get("position")
        out.created_at = o.get("created_at")
        return out


class Project:
    id: int
    name: str
    slug: str
    parent_id: None

    def __init__(self, _id: int, name: str, slug: str, parent_id: None) -> None:
        self.id = _id
        self.name = name
        self.slug = slug
        self.parent_id = parent_id

    @staticmethod
    def empty():
        return Project(None, None, None, None)

    @staticmethod
    def from_dict(o: dict):
        out = Project.empty()
        out.id = o.get("id")
        out.name = o.get("name")
        out.slug = o.get("slug")
        out.parent_id = o.get("parent_id")
        return out


class Status(Enum):
    FINISHED = "finished"
    IN_PROGRESS = "in_progress"


class ProjectsUser:
    id: int
    occurrence: int
    final_mark: Optional[int]
    status: Status
    validated: Optional[bool]
    current_team_id: int
    project: Project
    cursus_ids: List[int]
    marked_at: Optional[datetime]
    marked: bool
    retriable_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        _id: int,
        occurrence: int,
        final_mark: Optional[int],
        status: Status,
        validated: Optional[bool],
        current_team_id: int,
        project: Project,
        cursus_ids: List[int],
        marked_at: Optional[datetime],
        marked: bool,
        retriable_at: Optional[datetime],
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.id = _id
        self.occurrence = occurrence
        self.final_mark = final_mark
        self.status = status
        self.validated = validated
        self.current_team_id = current_team_id
        self.project = project
        self.cursus_ids = cursus_ids
        self.marked_at = marked_at
        self.marked = marked
        self.retriable_at = retriable_at
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def empty():
        return ProjectsUser(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    @staticmethod
    def from_dict(o: dict):
        out = ProjectsUser.empty()
        out.id = o.get("id")
        out.occurrence = o.get("occurrence")
        out.final_mark = o.get("final_mark")
        out.status = o.get("status")
        out.validated = o.get("validated")
        out.current_team_id = o.get("current_team_id")
        out.project = Project.from_dict(o.get("project"))
        out.cursus_ids = o.get("cursus_ids")
        out.marked_at = o.get("marked_at")
        out.marked = o.get("marked")
        out.retriable_at = o.get("retriable_at")
        out.created_at = o.get("created_at")
        out.updated_at = o.get("updated_at")
        return out


class User:
    id: int
    email: str
    login: str
    first_name: str
    last_name: str
    usual_full_name: str
    usual_first_name: None
    url: str
    phone: str
    displayname: str
    kind: str
    image: Image
    staff: bool
    correction_point: int
    pool_month: str
    pool_year: int
    location: str
    wallet: int
    anonymize_date: datetime
    data_erasure_date: datetime
    created_at: datetime
    updated_at: datetime
    alumnized_at: None
    alumni: bool
    active: bool
    groups: List[Any]
    cursus_users: List[CursusUser]
    projects_users: List[ProjectsUser]
    languages_users: List[LanguagesUser]
    achievements: List[Achievement]
    titles: List[Any]
    titles_users: List[Any]
    partnerships: List[Any]
    patroned: List[Any]
    patroning: List[Any]
    expertises_users: List[Any]
    roles: List[Any]
    campus: List[Campus]
    campus_users: List[CampusUser]

    def __init__(
        self,
        _id: int,
        email: str,
        login: str,
        first_name: str,
        last_name: str,
        usual_full_name: str,
        usual_first_name: None,
        url: str,
        phone: str,
        displayname: str,
        kind: str,
        image: Image,
        staff: bool,
        correction_point: int,
        pool_month: str,
        pool_year: int,
        location: str,
        wallet: int,
        anonymize_date: datetime,
        data_erasure_date: datetime,
        created_at: datetime,
        updated_at: datetime,
        alumnized_at: None,
        alumni: bool,
        active: bool,
        groups: List[Any],
        cursus_users: List[CursusUser],
        projects_users: List[ProjectsUser],
        languages_users: List[LanguagesUser],
        achievements: List[Achievement],
        titles: List[Any],
        titles_users: List[Any],
        partnerships: List[Any],
        patroned: List[Any],
        patroning: List[Any],
        expertises_users: List[Any],
        roles: List[Any],
        campus: List[Campus],
        campus_users: List[CampusUser],
    ) -> None:
        self.id = _id
        self.email = email
        self.login = login
        self.first_name = first_name
        self.last_name = last_name
        self.usual_full_name = usual_full_name
        self.usual_first_name = usual_first_name
        self.url = url
        self.phone = phone
        self.displayname = displayname
        self.kind = kind
        self.image = image
        self.staff = staff
        self.correction_point = correction_point
        self.pool_month = pool_month
        self.pool_year = pool_year
        self.location = location
        self.wallet = wallet
        self.anonymize_date = anonymize_date
        self.data_erasure_date = data_erasure_date
        self.created_at = created_at
        self.updated_at = updated_at
        self.alumnized_at = alumnized_at
        self.alumni = alumni
        self.active = active
        self.groups = groups
        self.cursus_users = cursus_users
        self.projects_users = projects_users
        self.languages_users = languages_users
        self.achievements = achievements
        self.titles = titles
        self.titles_users = titles_users
        self.partnerships = partnerships
        self.patroned = patroned
        self.patroning = patroning
        self.expertises_users = expertises_users
        self.roles = roles
        self.campus = campus
        self.campus_users = campus_users

    @staticmethod
    def empty():
        return User(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    @staticmethod
    def from_dict(o: dict):
        out = User.empty()
        out.id = o.get("id")
        out.email = o.get("email")
        out.login = o.get("login")
        out.first_name = o.get("first_name")
        out.last_name = o.get("last_name")
        out.usual_full_name = o.get("usual_full_name")
        out.usual_first_name = o.get("usual_first_name")
        out.url = o.get("url")
        out.phone = o.get("phone")
        out.displayname = o.get("displayname")
        out.kind = o.get("kind")
        out.image = Image.from_dict(o.get("image"))
        out.staff = o.get("staff")
        out.correction_point = o.get("correction_point")
        out.pool_month = o.get("pool_month")
        out.pool_year = o.get("pool_year")
        out.location = o.get("location")
        out.wallet = o.get("wallet")
        out.anonymize_date = o.get("anonymize_date")
        out.data_erasure_date = o.get("data_erasure_date")
        out.created_at = o.get("created_at")
        out.updated_at = o.get("updated_at")
        out.alumnized_at = o.get("alumnized_at")
        out.alumni = o.get("alumni")
        out.active = o.get("active")
        out.groups = [t for t in o.get("groups", [])]
        out.cursus_users = [
            CursusUser.from_dict(cu) for cu in o.get("cursus_users", [])
        ]
        out.projects_users = [
            ProjectsUser.from_dict(pu) for pu in o.get("projects_users", [])
        ]
        out.languages_users = [
            LanguagesUser.from_dict(lu) for lu in o.get("languages_users", [])
        ]
        out.achievements = [
            Achievement.from_dict(a) for a in o.get("achievements", [])
        ]
        out.titles = [t for t in o.get("titles", [])]
        out.titles_users = [t for t in o.get("titles_users", [])]
        out.partnerships = [t for t in o.get("partnerships", [])]
        out.patroned = [t for t in o.get("patroned", [])]
        out.patroning = [t for t in o.get("patroning", [])]
        out.expertises_users = [t for t in o.get("expertises_users", [])]
        out.roles = [t for t in o.get("roles", [])]
        out.campus = [Campus.from_dict(c) for c in o.get("campus", [])]
        out.campus_users = [
            CampusUser.from_dict(cu) for cu in o.get("campus_users", [])
        ]
        return out

    def find_project_user(self, term: str | int):
        for pu in self.projects_users:
            if term in [pu.project.name, pu.project.slug, pu.project.id, pu.id]:
                return pu
        return None
