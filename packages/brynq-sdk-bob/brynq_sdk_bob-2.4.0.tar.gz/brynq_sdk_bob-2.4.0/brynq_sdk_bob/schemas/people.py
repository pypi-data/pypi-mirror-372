from datetime import datetime
from typing import Optional

import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel



@extensions.register_check_method()
def check_list(x):
    return isinstance(x, list)


class PeopleSchema(BrynQPanderaDataFrameModel):
    id: Optional[Series[String]] = pa.Field(coerce=True, description="Person ID", alias="id")
    display_name: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Display Name", alias="displayName")
    company_id: Optional[Series[String]] = pa.Field(coerce=True, description="Company ID", alias="companyId")
    email: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Email", alias="email")
    home_mobile_phone: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Personal Mobile Phone", alias="home.mobilePhone")
    surname: Optional[Series[String]] = pa.Field(coerce=True, description="Surname", alias="surname")
    first_name: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="First Name", alias="firstName")
    full_name: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Full Name", alias="fullName")
    personal_birth_date: Optional[Series[DateTime]] = pa.Field(coerce=True, nullable=True, description="Personal Birth Date", alias="personal.birthDate")
    personal_pronouns: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Personal Pronouns", alias="personal.pronouns")
    personal_honorific: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Personal Honorific", alias="personal.honorific")
    personal_nationality: Optional[Series[object]] = pa.Field(coerce=True, check_name=check_list, description="Personal Nationality", alias="personal.nationality")
    # employee_payroll_manager: Series[String] = pa.Field(coerce=True, nullable=True)
    # employee_hrbp: Series[String] = pa.Field(coerce=True, nullable=True)
    # employee_it_admin: Series[String] = pa.Field(coerce=True, nullable=True)
    # employee_buddy: Series[String] = pa.Field(coerce=True, nullable=True)
    employee_veteran_status: Optional[Series[object]] = pa.Field(coerce=True, check_name=check_list, description="Employee Veteran Status", alias="employee.veteranStatus")
    employee_disability_status: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Employee Disability Status", alias="employee.disabilityStatus")
    work_start_date: Optional[Series[DateTime]] = pa.Field(coerce=True, nullable=True, description="Work Start Date", alias="work.startDate")
    work_manager: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Manager", alias="work.manager")
    work_work_phone: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Work Phone", alias="work.workPhone")
    work_tenure_duration_period_i_s_o: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Tenure Duration Period ISO", alias="work.tenureDurationPeriodIso")
    work_tenure_duration_sort_factor: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=False, description="Work Tenure Duration Sort Factor", alias="work.tenureDurationSortFactor")
    work_tenure_duration_humanize: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Tenure Duration Humanize", alias="work.tenureDurationHumanize")
    work_duration_of_employment_period_i_s_o: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Duration of Employment Period ISO", alias="work.durationOfEmploymentPeriodIso")
    work_duration_of_employment_sort_factor: Optional[Series[String]] = pa.Field(coerce=True, nullable=False, description="Work Duration of Employment Sort Factor", alias="work.durationOfEmploymentSortFactor")
    work_duration_of_employment_humanize: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Duration of Employment Humanize", alias="work.durationOfEmploymentHumanize")
    work_reports_to_id_in_company: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Work Reports to ID in Company", alias="work.reportsToIdInCompany")
    work_employee_id_in_company: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Work Employee ID in Company", alias="work.employeeIdInCompany")
    work_reports_to_display_name: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Reports to Display Name", alias="work.reportsToDisplayName")
    work_reports_to_email: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Reports to Email", alias="work.reportsToEmail")
    work_reports_to_surname: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Reports to Surname", alias="work.reportsToSurname")
    work_reports_to_first_name: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Reports to First Name", alias="work.reportsToFirstName")
    work_reports_to_id: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Work Reports to ID", alias="work.reportsToId")
    work_work_mobile: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Work Mobile", alias="work.workMobile")
    work_indirect_reports: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Work Indirect Reports", alias="work.indirectReports")
    work_site_id: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Work Site ID", alias="work.siteId")
    work_department: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Department", alias="work.department")
    work_tenure_duration_years: Optional[Series[Float]] = pa.Field(coerce=True, nullable=True, description="Work Tenure Duration Years", alias="work.tenureDurationYears")
    work_tenure_years: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Work Tenure Years", alias="work.tenureYears")
    work_is_manager: Optional[Series[Bool]] = pa.Field(coerce=True, nullable=True, description="Work Is Manager", alias="work.isManager")
    work_title: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Title", alias="work.title")
    work_site: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Site", alias="work.site")
    work_original_start_date: Optional[Series[DateTime]] = pa.Field(coerce=True, nullable=True, description="Work Original Start Date", alias="work.originalStartDate")
    work_active_effective_date: Optional[Series[DateTime]] = pa.Field(coerce=True, nullable=True, description="Work Active Effective Date", alias="work.activeEffectiveDate")
    work_direct_reports: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Work Direct Reports", alias="work.directReports")
    # work_work_change_type: Series[String] = pa.Field(coerce=True, nullable=True)
    work_second_level_manager: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Work Second Level Manager", alias="work.secondLevelManager")
    work_days_of_previous_service: Optional[Series[pd.Int64Dtype]] = pa.Field(coerce=True, nullable=True, description="Work Days of Previous Service", alias="work.daysOfPreviousService")
    work_years_of_service: Optional[Series[Float]] = pa.Field(coerce=True, nullable=True, description="Work Years of Service", alias="work.yearsOfService")
    payroll_employment_contract: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Contract Type", alias="payroll.employment.contract")
    payroll_employment_type: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Employment Type", alias="payroll.employment.type")
    tax_id: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Tax ID", alias="payroll.taxCode")

    about_food_preferences: Optional[Series[object]] = pa.Field(coerce=True, check_name=check_list, description="About Food Preferences", alias="about.foodPreferences")
    # about_social_data_linkedin: Series[String] = pa.Field(coerce=True, nullable=True)
    about_social_data_twitter: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="About Social Data Twitter", alias="about.socialDataTwitter")
    about_social_data_facebook: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="About Social Data Facebook", alias="about.socialDataFacebook")
    about_superpowers: Optional[Series[object]] = pa.Field(coerce=True, check_name=check_list, description="About Superpowers", alias="about.superpowers")
    about_hobbies: Optional[Series[object]] = pa.Field(coerce=True, check_name=check_list, description="About Hobbies", alias="about.hobbies")
    about_about: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="About About", alias="about.about")
    about_avatar: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="About Avatar", alias="about.avatar")
    address_city: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Address City", alias="address.city")
    address_post_code: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Address Post Code", alias="address.postCode")
    address_line1: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Address Line 1", alias="address.line1")
    address_line2: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Address Line 2", alias="address.line2")
    address_country: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Address Country", alias="address.country")
    address_active_effective_date: Optional[Series[DateTime]] = pa.Field(coerce=True, nullable=True, description="Address Active Effective Date", alias="address.activeEffectiveDate")
    home_legal_gender: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Legal Gender", alias="home.legalGender")
    home_family_status: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Family / Marital Status", alias="home.familyStatus")
    home_spouse_first_name: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Spouse First Name", alias="home.SpouseFirstName")
    home_spouse_surname: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Spouse Surname", alias="home.SpouseSurname")
    # home_spouse_birth_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    home_spouse_gender: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Spouse Gender", alias="home.SpouseGender")
    identification_ssn_serial_number: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="SSN Serial Number", alias="identification.ssnSerialNumber")
    internal_termination_reason: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Internal Termination Reason", alias="internal.terminationReason")
    internal_termination_date: Optional[Series[DateTime]] = pa.Field(coerce=True, nullable=True, description="Internal Termination Date", alias="internal.terminationDate")
    internal_termination_type: Optional[Series[String]] = pa.Field(coerce=True, nullable=True, description="Internal Termination Type", alias="internal.terminationType")
    employee_last_day_of_work: Optional[Series[DateTime]] = pa.Field(coerce=True, nullable=True, description="Employee Last Day of Work", alias="employee.lastDayOfWork")

    class Config:
        coerce = True
