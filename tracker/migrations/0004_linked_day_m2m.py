# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for item in orm.TrackingEntry.objects.all():
            item.delete()
            item.save()

    def backwards(self, orm):
        raise RuntimeError("Cannot go backwards.")

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
            'link': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'link_rel_+'", 'null': 'True', 'to': u"orm['tracker.TrackingEntry']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_tracking'", 'to': u"orm['tracker.Tbluser']"})
        }
    }

    complete_apps = ['tracker']
    symmetrical = True
