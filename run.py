import os
import requests
from lxml import html
from celery import Celery
from flask import Flask, request, jsonify, redirect
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
celery = Celery('run', backend='rpc://', broker='amqp://user:password@localhost//')
db = SQLAlchemy(app)
api = Api(app)


class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    html = db.Column(db.Text())
    success = db.Column(db.Boolean)


class ScrapingJob(Resource):
    def get(self, job_id):
        job = Job.query.filter_by(id=job_id).first()
        return {'success': job.success, 'html': job.html}
    def post(self, job_id):
        html = request.json.get('html')
        success = request.json.get('success')
        job = db.session.query(Job).filter_by(id=job_id).one()
        job.html = html
        job.success = success
        db.session.add(job)
        db.session.commit()
    def delete(self, job_id):
        job = Job.query.filter_by(id=job_id)
        db.session.delete(job)
        db.session.commmit()


@app.route('/', methods=['GET', 'PUT'])
def scraping_jobs_list():
    if request.method == 'PUT':
        url = request.json.get('url')
        success = False
        html = get_page.delay(url)
        if html.ready():
            success = True
        else:
            html = ''
        job = Job(html=html, success=success)
        db.session.add(job)
        db.session.commit()
        return 'successful put'
    elif request.method == 'GET':
        jobs_list = []
        jobs = Job.query.all()
        for job in jobs:
            jobs_list.append(
                {'id':job.id, 'html': job.html, 'success': job.success})
        return jsonify(jobs_list)


@celery.task
def get_page(url):
    page = requests.get(url, timeout=5)
    html_divs_content = html.fromstring(page.content).xpath('//div/text()')
    return html_divs_content


api.add_resource(ScrapingJob, '/<string:job_id>')


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run()
