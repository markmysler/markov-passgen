"""Command-line interface for markov-passgen"""

import click
from markov_passgen.core.corpus_loader import CorpusLoader
from markov_passgen.core.ngram_builder import NGramBuilder
from markov_passgen.core.generator import PasswordGenerator


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
    try:
        # Load corpus
        loader = CorpusLoader()
        click.echo(f"Loading corpus from {corpus}...")
        text = loader.load_from_file(corpus)
        
        # Validate corpus
        if not loader.validate_corpus(text):
            click.echo("Error: Corpus must be at least 100 characters", err=True)
            raise click.Abort()
        
        stats = loader.get_corpus_stats()
        click.echo(f"Corpus loaded: {stats['char_count']} chars, {stats['word_count']} words")
        
        # Build n-gram model
        click.echo("Building n-gram model...")
        builder = NGramBuilder()
        model = builder.build(text, n=2)
        click.echo(f"Model built with {len(model)} n-grams")
        
        # Generate passwords
        click.echo(f"Generating {count} passwords of length {length}...")
        generator = PasswordGenerator(model)
        passwords = generator.generate(count, length)
        
        # Write to output file
        with open(output, 'w', encoding='utf-8') as f:
            for password in passwords:
                f.write(password + '\n')
        
        click.echo(f"Successfully generated {len(passwords)} passwords to {output}")
        
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()
