"""Command-line interface for markov-passgen"""

import click


@click.group()
@click.version_option()
def main():
    """Markov Chain Password Generator"""
    pass


@main.command()
@click.option('--corpus', type=click.Path(exists=True), required=True, help='Path to corpus file')
@click.option('--count', default=100, help='Number of passwords to generate')
@click.option('--length', default=12, help='Password length')
@click.option('--output', default='wordlist.txt', help='Output file')
def generate(corpus, count, length, output):
    """Generate passwords from corpus"""
    raise NotImplementedError("Phase 1 implementation pending")


if __name__ == '__main__':
    main()
