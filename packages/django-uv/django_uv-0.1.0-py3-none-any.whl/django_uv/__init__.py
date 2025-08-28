from django.core.management import ManagementUtility


def main(argv=None) -> None:
    utility = ManagementUtility(argv)
    utility.execute()
