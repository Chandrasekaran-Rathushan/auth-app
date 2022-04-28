from django.utils import timezone


# def generateIdNo(module, prefix, isYear, suffixNo):
#     year = {True: timezone.now().year, False: ""}[isYear]
#     suffix = 0
#
#     try:
#         from pos.shopping_module.models import CustomIdNo
#         moduleRecordCount = CustomIdNo.objects.filter(module=module).count()
#         print("record => ", moduleRecordCount)
#         suffix = moduleRecordCount + 1
#     except:
#         suffix = suffix + 1
#
#     idString = f"{prefix}-{str(year)}{str(suffix)}"
#     return idString

# def generate_id(module, prefix, isYear):
#     module = module
#     prefix = prefix
#     isYear = isYear
#     year = {True: timezone.now().year, False: ""}[isYear]
#     suffix = 0
#
#     id = None
#
#     modules = [Customer, Product, Cart]
#
#     for m in modules:
#         if (m.__name__ == module):
#             try:
#                 o = m.Objects.filter()
#                 suffix = o.count() + 1
#             except m.DoesNotExist:
#                 suffix = suffix + 1
#             break
#
#     id = prefix + "-" + str(year) + str(suffix)
#
#     return id