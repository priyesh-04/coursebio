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
            print(key,len(value))


    	# for i in range(len(_cats)):
    	# 	print(_cats[i])
    	# 	cat = Category.objects.filter(title=_cats[i])
    	# 	print(cat,'hhh')
    	# 	if cat:
	    # 		courses = Course.objects.filter(category=cat[0])
	    # 		for j in range(len(courses)):
	    # 			sub_cat = SubCategory.objects.filter(course__title=courses[j].title)
	    # 			for k in range(len(sub_cat)):
	    # 				SubCategory.objects.filter(title=sub_cat[k].title).update(category=cat[0])

        return 'success'