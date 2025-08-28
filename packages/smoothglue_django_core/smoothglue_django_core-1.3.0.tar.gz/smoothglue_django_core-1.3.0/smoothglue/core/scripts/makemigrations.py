#!/usr/bin/env python

from django.core.management import call_command

from smoothglue.core.scripts.boot_django import boot_django

boot_django()
call_command("makemigrations", "core")
