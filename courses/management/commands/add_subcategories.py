# command to add subcategories

from django.core.management.base import BaseCommand, CommandError
from courses.models import Course, Category, SubCategory

class Command(BaseCommand):

    def handle(self, *args, **options):
        my_dict = {
                   "IT & Computer Science": ["Cloud Computing","Data Science", "Databases", "Desktop Development", "Game Development", "IT Certifications", "IT Operations & Devops", "Machine Learning",
                       "Mobile Development", "Network & Security", 
                       "Operating Systems", "Programming Languages", 
                       "Softwares & Tools", "Data Structures & Algorithms", 
                       "Software Engineering", "Software Testing", "Web Development"
                        ], 
                    "Arts & Design": ["Fashion", "Music Software", "Web Design", "Visual Arts", "Graphic Design", "Game Design", "Design Tools", "Product Design", "Film & Video", "Architecture & Interior Design", "Photography",
                        ], 
                    "Personal Development": ["Creativity", "Religion & Spirituality", "Productivity", "Memory & Study Skills", 
                        "Communication Skills", "Emotional Intelligence", 
                        "Parenting & Relationships", "Career & Interviewing", 
                        "Public Speaking", "Personal Finance",
                        ],
                    "Business": ["Communication", "Customer Service", 
                        "Home Business", "Sales", "Business Management Tools", 
                        "Business Intelligence & Analytics", "Entrepreneurship", 
                        "Leadership & Management", "Project Management", 
                        "Human Resources",
                    ],
                    "Math, Science & Engineering": ["Mechanical Engineering", 
                        "General Science", "Civil Engineering", "Electrical Engineering & Electronics", "Physics", "Chemistry",
                        "Mathematics", "Environmental Science", "Biology",
                    ],
                    "Professions & Hobbies": ["Travel", "Food & Beverage", 
                        "Beauty & Makeup", "Teaching & Education", "Crafts", 
                        "Gaming", "Real Estate",
                    ],
                    "Languages": ["Arabic Language", "English Language", 
                        "French Language", "Korean Language", 
                        "Japanese Language", "Italian Language", "Chinese Language", 
                        "Spanish Language", "German Language",
                    ],
                    "Marketing": ["Affiliate Marketing", "Branding", 
                        "Content Marketing", "Email Marketing", "SEO & SEM",
                        "Social Media",
                    ],
                    "Humanities & Social Sciences": ["Communication & Journalism", 
                        "Literature", "Sociology", "Law", "Geography", "Psychology", "Philosophy", "Economics", "History", 
                        "Political Science & Government",
                    ],
                    "Finance & Accounting": ["Finance Certification", 
                        "Accounting & Bookkeeping", "Investing & Trading", 
                        "Crypto & Blockchain",
                    ],
                    "Health & Fitness": ["Public Health", "Diseases & Disorders", 
                        "Sports", "Yoga", "Dance", "Self-defense", "Health Care",
                        "Nutrition", "Anatomy", "Meditation", "Mental Health",
                    ],
                    "Music": [],

                }

        for key, value in my_dict.items():
            # print(key,value)
            category_obj = Category.objects.filter(title=key).first()
            subcategories = value
            for item in subcategories:
                sub_cat = SubCategory.objects.filter(title=item)
                if not sub_cat:
                    subcategory_obj = SubCategory.objects.create(title=item)
                    subcategory_obj.category.add(category_obj)
                    subcategory_obj.save()
                else:
                    print("Sub category with this Title already exists.")

        return 'success'