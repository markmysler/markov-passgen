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
@click.option('--corpus', type=click.Path(exists=True), help='Path to single corpus file')
@click.option('--corpus-list', multiple=True, type=click.Path(exists=True), help='Paths to multiple corpus files (repeatable)')
@click.option('--corpus-weights', type=str, help='Comma-separated weights for each corpus (e.g., "1.0,2.0,1.5")')
@click.option('--count', default=100, help='Number of passwords to generate')
@click.option('--length', default=12, help='Password length')
@click.option('--ngram-size', default=2, type=click.IntRange(2, 5), help='N-gram size (2-5)')
@click.option('--min-length', type=int, help='Minimum password length')
@click.option('--max-length', type=int, help='Maximum password length')
@click.option('--require-digits', is_flag=True, help='Require at least one digit')
@click.option('--require-uppercase', is_flag=True, help='Require at least one uppercase letter')
@click.option('--require-lowercase', is_flag=True, help='Require at least one lowercase letter')
@click.option('--require-special', is_flag=True, help='Require at least one special character')
@click.option('--min-entropy', type=float, help='Minimum entropy threshold')
@click.option('--seed-word', type=str, help='Seed word to start generation')
@click.option('--random-seed', type=int, help='Random seed for deterministic generation')
@click.option('--lowercase', is_flag=True, help='Convert corpus to lowercase')
@click.option('--remove-punctuation', is_flag=True, help='Remove punctuation from corpus')
@click.option('--remove-digits', is_flag=True, help='Remove digits from corpus')
@click.option('--normalize-whitespace', is_flag=True, help='Normalize whitespace in corpus')
@click.option('--leet-speak', type=float, help='Apply leet speak transformation (0.0-1.0 intensity)')
@click.option('--case-variation', type=click.Choice(['random', 'alternating', 'capitalize']), help='Apply case variation')
@click.option('--output', default='wordlist.txt', help='Output file')
def generate(corpus, corpus_list, corpus_weights, count, length, ngram_size, min_length, max_length, 
             require_digits, require_uppercase, require_lowercase, require_special,
             min_entropy, seed_word, random_seed, lowercase, remove_punctuation,
             remove_digits, normalize_whitespace, leet_speak, case_variation, output):
    """Generate passwords from corpus"""
    try:
        from markov_passgen.filters.length_filter import LengthFilter
        from markov_passgen.filters.character_filter import CharacterFilter
        from markov_passgen.filters.filter_chain import FilterChain
        from markov_passgen.transformers.text_cleaner import TextCleaner
        from markov_passgen.transformers.password_transformer import (
            LeetSpeakTransformer, CaseVariationTransformer, TransformerChain
        )
        from markov_passgen.core.multi_corpus_manager import MultiCorpusManager
        
        # Validate corpus options
        if not corpus and not corpus_list:
            click.echo("Error: Must specify either --corpus or --corpus-list", err=True)
            raise click.Abort()
        
        if corpus and corpus_list:
            click.echo("Error: Cannot use both --corpus and --corpus-list", err=True)
            raise click.Abort()
        
        # Create text cleaner if any preprocessing options are set
        cleaner = None
        if lowercase or remove_punctuation or remove_digits or normalize_whitespace:
            cleaner = TextCleaner(
                lowercase=lowercase,
                remove_punctuation=remove_punctuation,
                remove_digits=remove_digits,
                normalize_whitespace=normalize_whitespace
            )
            click.echo("Text preprocessing enabled")
        
        # Load corpus - single or multi
        text = None
        if corpus_list:
            # Multi-corpus mode
            click.echo(f"Loading {len(corpus_list)} corpus files...")
            
            # Parse weights if provided
            weights = None
            if corpus_weights:
                try:
                    weights = [float(w.strip()) for w in corpus_weights.split(',')]
                    if len(weights) != len(corpus_list):
                        click.echo(f"Error: Number of weights ({len(weights)}) must match number of corpora ({len(corpus_list)})", err=True)
                        raise click.Abort()
                    click.echo(f"Using corpus weights: {weights}")
                except ValueError:
                    click.echo("Error: Invalid weight format. Use comma-separated numbers (e.g., '1.0,2.0,1.5')", err=True)
                    raise click.Abort()
            
            # Create multi-corpus manager
            manager = MultiCorpusManager.from_files(list(corpus_list), weights=weights, cleaner=cleaner)
            
            # Display corpus stats
            stats = manager.get_corpus_stats()
            for name, corpus_stats in stats.items():
                click.echo(f"  {name}: {corpus_stats['char_count']} chars, {corpus_stats['word_count']} words, weight={corpus_stats['weight']}")
            
            # Get merged corpus
            text = manager.get_merged_corpus()
            click.echo(f"Merged corpus: {len(text)} chars")
        else:
            # Single corpus mode
            loader = CorpusLoader()
            click.echo(f"Loading corpus from {corpus}...")
            text = loader.load_from_file(corpus, cleaner=cleaner)
            
            # Validate corpus
            if not loader.validate_corpus(text):
                click.echo("Error: Corpus must be at least 100 characters", err=True)
                raise click.Abort()
            
            stats = loader.get_corpus_stats()
            click.echo(f"Corpus loaded: {stats['char_count']} chars, {stats['word_count']} words")
        
        # Build n-gram model
        click.echo(f"Building {ngram_size}-gram model...")
        builder = NGramBuilder()
        model = builder.build(text, n=ngram_size)
        click.echo(f"Model built with {len(model)} n-grams")
        
        # Set random seed if specified
        generator = PasswordGenerator(model)
        if random_seed is not None:
            generator.set_random_seed(random_seed)
            click.echo(f"Using random seed: {random_seed}")
        
        # Create password transformer chain if any transformations are specified
        transformer_chain = None
        if leet_speak or case_variation:
            transformer_chain = TransformerChain()
            
            if leet_speak is not None:
                if not 0.0 <= leet_speak <= 1.0:
                    click.echo("Error: --leet-speak must be between 0.0 and 1.0", err=True)
                    raise click.Abort()
                transformer_chain.add(LeetSpeakTransformer(intensity=leet_speak))
                click.echo(f"Leet speak transformation enabled (intensity: {leet_speak})")
            
            if case_variation:
                transformer_chain.add(CaseVariationTransformer(mode=case_variation))
                click.echo(f"Case variation enabled (mode: {case_variation})")
        
        # Generate passwords
        if min_entropy:
            click.echo(f"Generating {count} passwords with min entropy {min_entropy}...")
            results = generator.generate_with_entropy(count, min_entropy)
            passwords = [pwd for pwd, _ in results]
            # Apply transformers to entropy-based passwords
            if transformer_chain:
                passwords = transformer_chain.transform_batch(passwords)
        else:
            click.echo(f"Generating {count} passwords of length {length}...")
            # Generate more than needed if we have filters
            multiplier = 10 if (min_length or max_length or require_digits or 
                               require_uppercase or require_lowercase or require_special) else 1
            passwords = generator.generate(count * multiplier, length, seed=seed_word, transformer=transformer_chain)
        
        # Apply filters
        if min_length or max_length or require_digits or require_uppercase or require_lowercase or require_special:
            click.echo("Applying filters...")
            filter_chain = FilterChain()
            
            # Length filter
            if min_length or max_length:
                min_len = min_length or 0
                max_len = max_length or 1000
                filter_chain.add_filter(LengthFilter(min_len, max_len))
            
            # Character filter
            if require_digits or require_uppercase or require_lowercase or require_special:
                filter_chain.add_filter(CharacterFilter(
                    require_digits=require_digits,
                    require_uppercase=require_uppercase,
                    require_lowercase=require_lowercase,
                    require_special=require_special
                ))
            
            passwords = filter_chain.apply(passwords)
            click.echo(f"After filtering: {len(passwords)} passwords")
            
            # Ensure we have enough
            if len(passwords) < count:
                click.echo(f"Warning: Only {len(passwords)} passwords meet filter criteria", err=True)
            
            passwords = passwords[:count]
        
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
