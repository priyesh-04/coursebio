# command to add subcategories

from django.core.management.base import BaseCommand, CommandError
from courses.models import Course, Category, SubCategory

class Command(BaseCommand):

    def handle(self, *args, **options):
        _cats = ["Professions & Hobbies", "Math, Science & Engineering", "Humanities & Social Sciences", "Languages", "Health & Fitness", "Arts & Design",    "Music", "Finance & Accounting", "Personal Development", "Marketing",
            "Business", "IT & Computer Science",
            ]

        print(_cats,len(_cats), 'categories_list')

        # for i in range(len(_cats)):
        #     print(_cats[i])
        #     cat = Category.objects.filter(title=_cats[i])
        #     print(cat,'hhh')
        #     if cat:
        #         courses = Course.objects.filter(category=cat[0])
        #         for j in range(len(courses)):
        #             sub_cat = SubCategory.objects.filter(course__title=courses[j].title)
        #             for k in range(len(sub_cat)):
        #                 SubCategory.objects.filter(title=sub_cat[k].title).update(category=cat[0])

        return 'success'