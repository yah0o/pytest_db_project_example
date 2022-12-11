from datetime import datetime

from npqa_db import DbClient
from npqa_report import step


class CatalogServiceDBSteps(object):
    def __init__(self, db_url):
        self.client = DbClient(db_url)

    @step
    def get_publish_task_status(self, publish_id):
        rows = self.client.execute(
            clause='select status from task where id = :publish_id',
            params=dict(publish_id=publish_id)).fetchall()
        status = None
        if rows:
            status = [row[0] for row in rows][0]
        return status

    @step
    def get_task_failure(self, publish_id):
        rows = self.client.execute(
            clause='select failure from task where id = :publish_id',
            params=dict(publish_id=publish_id)).fetchall()
        failure = None
        if rows:
            failure = [row[0] for row in rows][0]
        return failure

    @step
    def set_terminated_at_for_catalog(self, code):
        rows = self.client.execute(
            clause='select id from catalog where code = :code',
            params=dict(code=code))
        id = None
        if rows:
            id = [row[0] for row in rows][0]
        self.client.execute(
            clause='UPDATE catalog SET terminated_at = :current_time WHERE code = :code AND id = :id',
            params=dict(current_time=datetime.utcnow(), code=code, id=id))

    @step
    def get_new_title_from_db(self, full_title_id):
        rows = self.client.execute(
            clause='select code from title where full_title_id = :full_title_id',
            params=dict(full_title_id=full_title_id)).fetchall()
        code = None
        if rows:
            code = [row[0] for row in rows][0]
        return code

    @step
    def update_publish_status_in_db(self, catalog_publish_id, status):
        self.client.execute(
            clause='update task set status = :status where catalog_id =:catalog_publish_id',
            params=dict(catalog_publish_id=catalog_publish_id, status=status))

    @step
    def add_new_entity_data_into_db(self, entity_id, code, etype, fields, metadata):
        self.client.execute(
            clause='insert into entity_data (entity_id, code, etype, fields, metadata) values(:entity_id, :code, :etype, :fields, :metadata)'
                   'on conflict do nothing',
            params=dict(entity_id=entity_id, code=code, etype=etype, fields=fields, metadata=metadata))

    @step
    def get_task_processing_time(self, publish_id):
        task_processing_time = self.client.execute(
            clause='select started_at, finished_at from task where id = :publish_id',
            params=dict(publish_id=publish_id)).fetchall()
        if task_processing_time:
            started_at = task_processing_time[0][0]
            finished_at = task_processing_time[0][1]
        catalog_processing_time = self.client.execute(
            clause='select c.activated_at, c.terminated_at from catalog c join task t ON t.catalog_id = c.id where t.id = :publish_id',
            params=dict(publish_id=publish_id)).fetchall()
        if catalog_processing_time:
            activated_at = catalog_processing_time[0][0]
            terminated_at = catalog_processing_time[0][1]
        result = {'started_at': started_at, 'finished_at': finished_at,
                  'activated_at': activated_at, 'terminated_at': terminated_at}
        return result

    @step
    def get_global_property(self, property_id):
        status_node = self.client.execute(
            clause='select * from global_property where id = :property_id',
            params=dict(property_id=property_id)).fetchall()
        if status_node:
            node_value = status_node[0][1]
            node_description = status_node[0][2]
        result = {'node_value': node_value, 'description': node_description}
        return result

    @step
    def delete_publish_task(self, task_id):
        self.client.execute(
            clause='DELETE from task where id = :task_id',
            params=dict(task_id=task_id))

    @step
    def add_publish_task(self, task):
        self.client.execute(
            clause='insert into task(id, title_id, catalog_code, publisher, status, created_at, tracking_id, url, node) '
                   ' values(:id, :title_id, :catalog_code, :publisher, :status, :created_at, :tracking_id, :url, :node)',
            params=task)

    @step
    def get_active_catalogs(self, catalog_type):
        catalog_codes = self.client.execute(
            clause='select code from catalog where terminated_at is NULL AND NOT activated_at '
                   'is NULL and ctype = :catalog_type', params=dict(catalog_type=catalog_type)).fetchall()
        result = []
        for i in catalog_codes:
            result.append(i[0])
        return result

    @step
    def get_catalog_by_catalog_code(self, catalog_code):
        result = []
        catalog = self.client.execute(
            clause='select * from catalog where code =:catalog_code', params=dict(catalog_code=catalog_code)).fetchall()
        if catalog:
            result = {'catalog_code': catalog[0][1],
                      'activated_at': catalog[0][2], 'terminated_at':  catalog[0][3]}
        return result
