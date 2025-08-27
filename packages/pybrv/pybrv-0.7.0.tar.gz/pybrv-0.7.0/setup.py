from setuptools import setup, find_namespace_packages

setup(
    name="pybrv",
    version="0.7.0",
    description="Python Business Rule Validator",
    author="Puneet Taneja",
    packages=find_namespace_packages(include=["pybrv*"]),
    include_package_data=True,
    package_data={
        "pybrv.sql_templates.business_rule_check": ["*.sql"],
        "pybrv.sql_templates.common": ["*.sql"],
    },
    install_requires=[
        "pandas>=1.3.0",
        "sqlalchemy>=1.4.0",
        "psycopg2-binary>=2.9.0",
        "python-dotenv>=0.19.0",
        "databricks-sql-connector>=2.0.0",
        "pytz>=2021.1",
        "retry>=0.9.2",
        "openAI"
    ],
    entry_points={
        "console_scripts": [
            "pybrv=pybrv.main:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
