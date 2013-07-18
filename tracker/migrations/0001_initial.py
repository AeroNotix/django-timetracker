# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tbluser'
        db.create_table(u'tbluser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=105)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=60, db_column='uFirstName')),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=60, db_column='uLastName')),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=60, db_column='uPassword')),
            ('user_type', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('market', self.gf('django.db.models.fields.CharField')(max_length=2, db_column='uMarket')),
            ('process', self.gf('django.db.models.fields.CharField')(max_length=2, db_column='uProcess')),
            ('start_date', self.gf('django.db.models.fields.DateField')(db_column='Start_Date')),
            ('breaklength', self.gf('django.db.models.fields.TimeField')(db_column='breakLength')),
            ('shiftlength', self.gf('django.db.models.fields.TimeField')(db_column='shiftLength')),
            ('job_code', self.gf('django.db.models.fields.CharField')(max_length=6, db_column='Job_Code')),
            ('holiday_balance', self.gf('django.db.models.fields.IntegerField')(db_column='Holiday_Balance')),
            ('disabled', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='disabled')),
        ))
        db.send_create_signal(u'tracker', ['Tbluser'])

        # Adding model 'RelatedUsers'
        db.create_table(u'tblrelatedusers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='related_foreign', to=orm['tracker.Tbluser'])),
        ))
        db.send_create_signal(u'tracker', ['RelatedUsers'])

        # Adding M2M table for field users on 'RelatedUsers'
        m2m_table_name = db.shorten_name(u'tblrelatedusers_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('relatedusers', models.ForeignKey(orm[u'tracker.relatedusers'], null=False)),
            ('tbluser', models.ForeignKey(orm[u'tracker.tbluser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['relatedusers_id', 'tbluser_id'])

        # Adding model 'Tblauthorization'
        db.create_table(u'tblauthorization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='admin_foreign', to=orm['tracker.Tbluser'])),
        ))
        db.send_create_signal(u'tracker', ['Tblauthorization'])

        # Adding M2M table for field users on 'Tblauthorization'
        m2m_table_name = db.shorten_name(u'tblauthorization_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tblauthorization', models.ForeignKey(orm[u'tracker.tblauthorization'], null=False)),
            ('tbluser', models.ForeignKey(orm[u'tracker.tbluser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tblauthorization_id', 'tbluser_id'])

        # Adding model 'TrackingEntry'
        db.create_table(u'tracker_trackingentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_tracking', to=orm['tracker.Tbluser'])),
            ('link', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='linked_entry', unique=True, null=True, to=orm['tracker.TrackingEntry'])),
            ('entry_date', self.gf('django.db.models.fields.DateField')()),
            ('start_time', self.gf('django.db.models.fields.TimeField')()),
            ('end_time', self.gf('django.db.models.fields.TimeField')()),
            ('breaks', self.gf('django.db.models.fields.TimeField')()),
            ('daytype', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'tracker', ['TrackingEntry'])

        # Adding unique constraint on 'TrackingEntry', fields ['user', 'entry_date']
        db.create_unique(u'tracker_trackingentry', ['user_id', 'entry_date'])


    def backwards(self, orm):
        # Removing unique constraint on 'TrackingEntry', fields ['user', 'entry_date']
        db.delete_unique(u'tracker_trackingentry', ['user_id', 'entry_date'])

        # Deleting model 'Tbluser'
        db.delete_table(u'tbluser')

        # Deleting model 'RelatedUsers'
        db.delete_table(u'tblrelatedusers')

        # Removing M2M table for field users on 'RelatedUsers'
        db.delete_table(db.shorten_name(u'tblrelatedusers_users'))

        # Deleting model 'Tblauthorization'
        db.delete_table(u'tblauthorization')

        # Removing M2M table for field users on 'Tblauthorization'
        db.delete_table(db.shorten_name(u'tblauthorization_users'))

        # Deleting model 'TrackingEntry'
        db.delete_table(u'tracker_trackingentry')


    models = {
        u'tracker.relatedusers': {
            'Meta': {'object_name': 'RelatedUsers', 'db_table': "u'tblrelatedusers'"},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_foreign'", 'to': u"orm['tracker.Tbluser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_view'", 'symmetrical': 'False', 'to': u"orm['tracker.Tbluser']"})
        },
        u'tracker.tblauthorization': {
            'Meta': {'object_name': 'Tblauthorization', 'db_table': "u'tblauthorization'"},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admin_foreign'", 'to': u"orm['tracker.Tbluser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subordinates'", 'symmetrical': 'False', 'to': u"orm['tracker.Tbluser']"})
        },
        u'tracker.tbluser': {
            'Meta': {'ordering': "['user_id']", 'object_name': 'Tbluser', 'db_table': "u'tbluser'"},
            'breaklength': ('django.db.models.fields.TimeField', [], {'db_column': "'breakLength'"}),
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'disabled'"}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '60', 'db_column': "'uFirstName'"}),
            'holiday_balance': ('django.db.models.fields.IntegerField', [], {'db_column': "'Holiday_Balance'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_code': ('django.db.models.fields.CharField', [], {'max_length': '6', 'db_column': "'Job_Code'"}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '60', 'db_column': "'uLastName'"}),
            'market': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_column': "'uMarket'"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '60', 'db_column': "'uPassword'"}),
            'process': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_column': "'uProcess'"}),
            'shiftlength': ('django.db.models.fields.TimeField', [], {'db_column': "'shiftLength'"}),
            'start_date': ('django.db.models.fields.DateField', [], {'db_column': "'Start_Date'"}),
            'user_id': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '105'}),
            'user_type': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        u'tracker.trackingentry': {
            'Meta': {'ordering': "['user']", 'unique_together': "(('user', 'entry_date'),)", 'object_name': 'TrackingEntry'},
            'breaks': ('django.db.models.fields.TimeField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'daytype': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'entry_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'linked_entry'", 'unique': 'True', 'null': 'True', 'to': u"orm['tracker.TrackingEntry']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_tracking'", 'to': u"orm['tracker.Tbluser']"})
        }
    }

    complete_apps = ['tracker']