from django.test import TestCase
from contact.forms import ContactForm
from contact.models import Contact

def create_form(email):
    contact = Contact.objects.get(email=email)
    form = ContactForm({"email": contact.email, "subject": contact.subject, "message": contact.message})
    return form


class ContactTest(TestCase):

    def setUp(self) -> None:
        Contact.objects.create(email="testuser@gmail.com", subject="TestSubject",
                               message="Hello World! I Like your catering!")
        Contact.objects.create(email="notGoodEmailFormat", subject="TestForm",
                               message="Hello World! I Like your catering, i have wrong email format!")

    def test_contact_created_properly(self) -> None:
        contact = Contact.objects.get(email="testuser@gmail.com")
        self.assertEqual(contact.email, "testuser@gmail.com")
        self.assertEqual(contact.subject, "TestSubject")
        self.assertEqual(contact.message, "Hello World! I Like your catering!")

    def test_form(self)->None:
        contact = Contact.objects.get(email="testuser@gmail.com")
        form = create_form(contact.email)
        self.assertTrue(form.is_valid())

    def test_email_field(self):
        contact = Contact.objects.get(email="notGoodEmailFormat")
        form = create_form(contact.email)
        self.assertEqual(form.errors['email'][0], 'Enter a valid email address.')

    def tearDown(self) -> None:
        Contact.objects.filter(email="testuser@gmail.com").delete()
        Contact.objects.filter(email="notGoodEmailFormat").delete()
