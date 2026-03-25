#from django.test import TestCase

# Create your tests here.
from core.dispatcher import SourceDispatcher
   

print(SourceDispatcher.process_file("C:\\Users\\Kalinkin\\Desktop\\AI_assistent\\requirements.txt"))
print(SourceDispatcher.process_file("C:\\Users\\Kalinkin\\Desktop\\AI_assistent\\popexplosives.pdf"))