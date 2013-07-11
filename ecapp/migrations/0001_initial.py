# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Folder'
        db.create_table('ecapp_folder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecapp.Folder'], null=True, blank=True)),
            ('import_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('ecapp', ['Folder'])

        # Adding unique constraint on 'Folder', fields ['name', 'parent']
        db.create_unique('ecapp_folder', ['name', 'parent_id'])

        # Adding model 'DesignStep'
        db.create_table('ecapp_designstep', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('step_number', self.gf('django.db.models.fields.IntegerField')()),
            ('procedure', self.gf('django.db.models.fields.TextField')()),
            ('expected', self.gf('django.db.models.fields.TextField')()),
            ('comments', self.gf('django.db.models.fields.TextField')()),
            ('import_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal('ecapp', ['DesignStep'])

        # Adding model 'UploadedFile'
        db.create_table('ecapp_uploadedfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=150, blank=True)),
        ))
        db.send_create_signal('ecapp', ['UploadedFile'])

        # Adding model 'TestCase'
        db.create_table('ecapp_testcase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='author', to=orm['auth.User'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_automated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('default_assignee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('folder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecapp.Folder'], null=True)),
            ('added_version', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('deprecated_version', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('bug_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('updated_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='updated_by', null=True, to=orm['auth.User'])),
            ('related_testcase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecapp.TestCase'], null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(default='P', max_length=1, null=True, blank=True)),
            ('test_script_file', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('method_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('import_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('product', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('feature', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('case_type', self.gf('django.db.models.fields.CharField')(default='Regression', max_length=30, null=True, blank=True)),
            ('folder_path', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal('ecapp', ['TestCase'])

        # Adding M2M table for field design_steps on 'TestCase'
        m2m_table_name = db.shorten_name('ecapp_testcase_design_steps')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('testcase', models.ForeignKey(orm['ecapp.testcase'], null=False)),
            ('designstep', models.ForeignKey(orm['ecapp.designstep'], null=False))
        ))
        db.create_unique(m2m_table_name, ['testcase_id', 'designstep_id'])

        # Adding M2M table for field uploads on 'TestCase'
        m2m_table_name = db.shorten_name('ecapp_testcase_uploads')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('testcase', models.ForeignKey(orm['ecapp.testcase'], null=False)),
            ('uploadedfile', models.ForeignKey(orm['ecapp.uploadedfile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['testcase_id', 'uploadedfile_id'])

        # Adding model 'TestPlan'
        db.create_table('ecapp_testplan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='creator', to=orm['auth.User'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('schedule', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('release', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('leader', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
        ))
        db.send_create_signal('ecapp', ['TestPlan'])

        # Adding model 'TestplanTestcaseLink'
        db.create_table('ecapp_testplantestcaselink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('testcase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecapp.TestCase'])),
            ('testplan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecapp.TestPlan'])),
        ))
        db.send_create_signal('ecapp', ['TestplanTestcaseLink'])

        # Adding unique constraint on 'TestplanTestcaseLink', fields ['testcase', 'testplan']
        db.create_unique('ecapp_testplantestcaselink', ['testcase_id', 'testplan_id'])

        # Adding model 'Result'
        db.create_table('ecapp_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('testplan_testcase_link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ecapp.TestplanTestcaseLink'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='failed', max_length=10)),
            ('environment', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('tester', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('ninja_id', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('bug_ticket', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('latest', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('ecapp', ['Result'])


    def backwards(self, orm):
        # Removing unique constraint on 'TestplanTestcaseLink', fields ['testcase', 'testplan']
        db.delete_unique('ecapp_testplantestcaselink', ['testcase_id', 'testplan_id'])

        # Removing unique constraint on 'Folder', fields ['name', 'parent']
        db.delete_unique('ecapp_folder', ['name', 'parent_id'])

        # Deleting model 'Folder'
        db.delete_table('ecapp_folder')

        # Deleting model 'DesignStep'
        db.delete_table('ecapp_designstep')

        # Deleting model 'UploadedFile'
        db.delete_table('ecapp_uploadedfile')

        # Deleting model 'TestCase'
        db.delete_table('ecapp_testcase')

        # Removing M2M table for field design_steps on 'TestCase'
        db.delete_table(db.shorten_name('ecapp_testcase_design_steps'))

        # Removing M2M table for field uploads on 'TestCase'
        db.delete_table(db.shorten_name('ecapp_testcase_uploads'))

        # Deleting model 'TestPlan'
        db.delete_table('ecapp_testplan')

        # Deleting model 'TestplanTestcaseLink'
        db.delete_table('ecapp_testplantestcaselink')

        # Deleting model 'Result'
        db.delete_table('ecapp_result')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ecapp.designstep': {
            'Meta': {'object_name': 'DesignStep'},
            'comments': ('django.db.models.fields.TextField', [], {}),
            'expected': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'procedure': ('django.db.models.fields.TextField', [], {}),
            'step_number': ('django.db.models.fields.IntegerField', [], {})
        },
        'ecapp.folder': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'Folder'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecapp.Folder']", 'null': 'True', 'blank': 'True'})
        },
        'ecapp.result': {
            'Meta': {'object_name': 'Result'},
            'bug_ticket': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'environment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'ninja_id': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'failed'", 'max_length': '10'}),
            'tester': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'testplan_testcase_link': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecapp.TestplanTestcaseLink']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'ecapp.testcase': {
            'Meta': {'object_name': 'TestCase'},
            'added_version': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'author'", 'to': "orm['auth.User']"}),
            'bug_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'case_type': ('django.db.models.fields.CharField', [], {'default': "'Regression'", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'deprecated_version': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'design_steps': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ecapp.DesignStep']", 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'feature': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecapp.Folder']", 'null': 'True'}),
            'folder_path': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'is_automated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'method_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'priority': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'related_testcase': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecapp.TestCase']", 'null': 'True', 'blank': 'True'}),
            'test_script_file': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'updated_by'", 'null': 'True', 'to': "orm['auth.User']"}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'uploads': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ecapp.UploadedFile']", 'null': 'True', 'blank': 'True'})
        },
        'ecapp.testplan': {
            'Meta': {'object_name': 'TestPlan'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'creator'", 'to': "orm['auth.User']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'release': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'schedule': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'testcases': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ecapp.TestCase']", 'null': 'True', 'through': "orm['ecapp.TestplanTestcaseLink']", 'blank': 'True'})
        },
        'ecapp.testplantestcaselink': {
            'Meta': {'unique_together': "(('testcase', 'testplan'),)", 'object_name': 'TestplanTestcaseLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'testcase': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecapp.TestCase']"}),
            'testplan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecapp.TestPlan']"})
        },
        'ecapp.uploadedfile': {
            'Meta': {'object_name': 'UploadedFile'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'blank': 'True'})
        }
    }

    complete_apps = ['ecapp']