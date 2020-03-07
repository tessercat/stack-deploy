{
    'ADMINS': (
        ('Firewall admin', '{{ admin_email }}'),
     ),
    'SERVER_EMAIL': 'noreply@{{ hostname }}',
    'TIME_ZONE': '{{ timezone }}',
}
