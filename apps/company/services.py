from apps.company.models import Company

def get_company():
    return Company.objects.first()

def update_company(data, logo=None):
    company = Company.objects.first()
    if not company:
        company = Company()

    for attr, value in data.items():
        setattr(company, attr, value)

    if logo:
        company.logo = logo

    company.save()
    return company
