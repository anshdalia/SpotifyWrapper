from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from mainApp.models import Wrap, TopArtist, TopSong


class Command(BaseCommand):
    help = 'Creates sample Wrapped data for testing'

    def handle(self, *args, **options):
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )

        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created test user: {user.username}'))

        # Create a Wrap for the current year
        current_year = timezone.now().year
        wrap, created = Wrap.objects.get_or_create(
            user=user,
            year=current_year,
            defaults={
                'minutes_listened': 54380,
                'top_genre': 'Pop'
            }
        )

        # Sample top artists
        artists = [
            {'name': 'Taylor Swift', 'rank': 1, 'image_url': '/api/placeholder/60/60'},
            {'name': 'The Weeknd', 'rank': 2, 'image_url': '/api/placeholder/60/60'},
            {'name': 'Drake', 'rank': 3, 'image_url': '/api/placeholder/60/60'},
            {'name': 'Arctic Monkeys', 'rank': 4, 'image_url': '/api/placeholder/60/60'},
            {'name': 'Lana Del Rey', 'rank': 5, 'image_url': '/api/placeholder/60/60'},
        ]

        # Sample top songs
        songs = [
            {'title': 'Anti-Hero', 'artist': 'Taylor Swift', 'rank': 1, 'image_url': '/api/placeholder/60/60'},
            {'title': 'Blinding Lights', 'artist': 'The Weeknd', 'rank': 2, 'image_url': '/api/placeholder/60/60'},
            {'title': 'Rich Flex', 'artist': 'Drake', 'rank': 3, 'image_url': '/api/placeholder/60/60'},
            {'title': 'R U Mine?', 'artist': 'Arctic Monkeys', 'rank': 4, 'image_url': '/api/placeholder/60/60'},
            {'title': 'Born To Die', 'artist': 'Lana Del Rey', 'rank': 5, 'image_url': '/api/placeholder/60/60'},
        ]

        # Clear existing data
        TopArtist.objects.filter(wrap=wrap).delete()
        TopSong.objects.filter(wrap=wrap).delete()

        # Create new artists
        for artist_data in artists:
            TopArtist.objects.create(wrap=wrap, **artist_data)
            self.stdout.write(f'Created artist: {artist_data["name"]}')

        # Create new songs
        for song_data in songs:
            TopSong.objects.create(wrap=wrap, **song_data)
            self.stdout.write(f'Created song: {song_data["title"]}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample Wrapped data'))