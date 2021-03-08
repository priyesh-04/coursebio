# command to add subcategories

from django.core.management.base import BaseCommand, CommandError
from courses.models import Course, Category, SubCategory

class Command(BaseCommand):

    def handle(self, *args, **options):
        _cats = ["Professions & Hobbies", "Math, Science & Engineering", "Humanities & Social Sciences", "Languages", "Health & Fitness", "Arts & Design",    "Music", "Finance & Accounting", "Personal Development", "Marketing",
            "Business", "IT & Computer Science",
            ]


        for i in range(len(_cats)):
            cat = Category.objects.filter(title=_cats[i])
            # try:
            #     category = Category.objects.create(title=_cats[i])
            # except Exception as e:
            #     print(e,"Category with this Title already exists.",'Exception line 21')
            if not cat:
                category_obj = Category.objects.create(title=_cats[i])
                category_obj.save()
            else:
                print("Category with this Title already exists.")

        return 'success'