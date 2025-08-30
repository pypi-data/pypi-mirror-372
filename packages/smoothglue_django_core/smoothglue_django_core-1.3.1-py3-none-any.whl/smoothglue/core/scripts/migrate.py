#!/usr/bin/env python

from django.core.management import call_command

from smoothglue.core.scripts.boot_django import boot_django

# call the django setup routine
boot_django()

call_command("migrate")
