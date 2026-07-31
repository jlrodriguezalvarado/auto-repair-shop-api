from apps.company.models import Company

def get_user_company(user):
    if not user or not getattr(user, "company_id", None):
        return None
    return user.company

def update_user_company(user, data, logo=None):
    company = get_user_company(user)
    if not company:
        return None
    allowed = {"name", "tax_id", "address", "phone", "secondary_phone", "email"}
    for attr, value in data.items():
        if attr in allowed:
            setattr(company, attr, value)
    if logo is not None:
        company.logo = logo
    company.save()
    return company
