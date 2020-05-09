import click
from HW3 import Patient, PatientCollection
    
@click.group()
def cli():
    """Создаем пациентов через консоль"""
@click.command('create')
@click.argument('first-name')
@click.argument('last-name')
@click.option('--birth-date', help='The birth date format "yyyy-mm-dd"')
@click.option('--phone', help='The phone format "8-ddd-ddd-dd-dd"')
@click.option('--document-type', help='The document type must be "Паспорт", "Заграничный паспорт",'
                                        ' "Водительские права"')
@click.option('--document-number', help='The document id must have 10 digits for russian passport or driving licence'
                                        'or 9 digits for international passport')

def create_patient(first_name, last_name, birth_date, phone, document_type, document_number):
    p = Patient(first_name, last_name, birth_date, phone, document_type, document_number)
    p.save()


@click.command('show')
@click.argument('num', default=10)
def show_patients(num):
    pc = PatientCollection()
    for m in pc.limit(num):
        click.echo(m)


@click.command('count')
# @click.argument('num', default=10)
def count_patients():
    pc = PatientCollection()
    count=0
    for m in pc:
        count+=1
    click.echo(count)



cli.add_command(create_patient)
cli.add_command(show_patients)
cli.add_command(count_patients)
cli()

