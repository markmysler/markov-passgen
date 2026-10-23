"""Command-line interface for markov-passgen"""

import click

from markov_passgen.core.corpus_loader import CorpusLoader
from markov_passgen.core.generator import PasswordGenerator
from markov_passgen.core.ngram_builder import NGramBuilder


@click.group()
@click.version_option()
def main():
    """Markov Chain Password Generator"""
    pass


@main.command()
@click.option('--corpus', type=click.Path(exists=True), help='Path to corpus file', required=True)
@click.option('--ngram-size', default=2, type=click.IntRange(2, 5), help='N-gram size (2-5)')
@click.option('--ngram-freq', type=click.Path(), help='Output path for n-gram frequency plot')
@click.option('--char-dist', type=click.Path(), help='Output path for character distribution plot')
@click.option('--top-n', default=20, type=int, help='Number of top items to display in plots')
def visualize_corpus(corpus, ngram_size, ngram_freq, char_dist, top_n):
    """Visualize corpus n-gram and character distributions"""
    try:
        from markov_passgen.visualization.visualizer import NGramVisualizer

        # Load corpus
        loader = CorpusLoader()
        click.echo(f"Loading corpus from {corpus}...")
        text = loader.load_from_file(corpus)

        if not loader.validate_corpus(text):
            click.echo("Error: Corpus must be at least 100 characters", err=True)
            raise click.Abort()

        # Build n-gram model
        builder = NGramBuilder()
        model = builder.build(text, n=ngram_size)
        click.echo(f"Built {ngram_size}-gram model with {len(model)} n-grams")

        # Create visualizer
        visualizer = NGramVisualizer()

        # Plot n-gram frequencies
        if ngram_freq:
            click.echo("Generating n-gram frequency plot...")
            visualizer.plot_ngram_frequencies(model, top_n=top_n, output_path=ngram_freq)
            click.echo(f"N-gram frequency plot saved to {ngram_freq}")

        # Plot character distribution
        if char_dist:
            click.echo("Generating character distribution plot...")
            visualizer.plot_character_distribution(text, top_n=top_n, output_path=char_dist)
            click.echo(f"Character distribution plot saved to {char_dist}")

        if not ngram_freq and not char_dist:
            click.echo("No visualization output specified. Use --ngram-freq or --char-dist", err=True)

    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.command()
@click.option('--wordlist', type=click.Path(exists=True), required=True, help='Path to password wordlist file')
@click.option('--entropy-dist', type=click.Path(), help='Output path for entropy distribution plot')
@click.option('--length-dist', type=click.Path(), help='Output path for length distribution plot')
@click.option('--bins', default=30, type=int, help='Number of histogram bins')
def visualize_passwords(wordlist, entropy_dist, length_dist, bins):
    """Visualize password entropy and length distributions"""
    try:
        from markov_passgen.core.entropy_calculator import EntropyCalculator
        from markov_passgen.visualization.visualizer import NGramVisualizer

        # Load passwords
        click.echo(f"Loading passwords from {wordlist}...")
        with open(wordlist, 'r', encoding='utf-8') as f:
            passwords = [line.strip() for line in f if line.strip()]

        if not passwords:
            click.echo("Error: Wordlist is empty", err=True)
            raise click.Abort()

        click.echo(f"Loaded {len(passwords)} passwords")

        # Create visualizer
        visualizer = NGramVisualizer()

        # Plot entropy distribution
        if entropy_dist:
            click.echo("Generating entropy distribution plot...")
            entropy_calc = EntropyCalculator()
            visualizer.plot_entropy_distribution(passwords, entropy_calc, bins=bins, output_path=entropy_dist)
            click.echo(f"Entropy distribution plot saved to {entropy_dist}")

        # Plot length distribution
        if length_dist:
            click.echo("Generating length distribution plot...")
            visualizer.plot_length_distribution(passwords, bins=bins, output_path=length_dist)
            click.echo(f"Length distribution plot saved to {length_dist}")

        if not entropy_dist and not length_dist:
            click.echo("No visualization output specified. Use --entropy-dist or --length-dist", err=True)

    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.command()
@click.option('--corpus-list', multiple=True, type=click.Path(exists=True), required=True,
              help='Paths to corpus files (repeatable)')
@click.option('--corpus-weights', type=str, help='Comma-separated weights for each corpus (e.g., "1.0,2.0,1.5")')
@click.option('--output', type=click.Path(), required=True, help='Output path for corpus comparison plot')
def visualize_multi_corpus(corpus_list, corpus_weights, output):
    """Visualize comparison of multiple corpora"""
    try:
        from markov_passgen.core.multi_corpus_manager import MultiCorpusManager
        from markov_passgen.visualization.visualizer import NGramVisualizer

        click.echo(f"Loading {len(corpus_list)} corpus files...")

        # Parse weights if provided
        weights = None
        if corpus_weights:
            try:
                weights = [float(w.strip()) for w in corpus_weights.split(',')]
                if len(weights) != len(corpus_list):
                    click.echo(f"Error: Number of weights ({len(weights)}) must match "
                           f"number of corpora ({len(corpus_list)})", err=True)
                    raise click.Abort()
            except ValueError:
                click.echo("Error: Invalid weight format. Use comma-separated numbers "
                           "(e.g., '1.0,2.0,1.5')", err=True)
                raise click.Abort() from None

        # Create multi-corpus manager
        manager = MultiCorpusManager.from_files(list(corpus_list), weights=weights)

        # Get corpus statistics
        stats = manager.get_corpus_stats()
        click.echo(f"Loaded {len(stats)} corpora")

        # Create visualizer
        visualizer = NGramVisualizer()

        # Plot corpus comparison
        click.echo("Generating corpus comparison plot...")
        visualizer.plot_corpus_comparison(stats, output_path=output)
        click.echo(f"Corpus comparison plot saved to {output}")

    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


def _corpus_options(func):
    """Options for reading corpora and building a model (shared by train and generate)"""
    options = [
        click.option('--corpus', type=click.Path(exists=True), help='Path to single corpus file'),
        click.option('--corpus-list', multiple=True, type=click.Path(exists=True),
                     help='Paths to multiple corpus files (repeatable)'),
        click.option('--corpus-weights', type=str,
                     help="Comma-separated weights, each corpus's share of the model (e.g. \"0.5,0.3,0.2\")"),
        click.option('--ngram-size', default=2, type=click.IntRange(2, 5), help='N-gram size (2-5)'),
        click.option('--stream', is_flag=True,
                     help='Read the corpus as one continuous text instead of one entry per line'),
        click.option('--lowercase', is_flag=True, help='Convert corpus to lowercase'),
        click.option('--remove-punctuation', is_flag=True, help='Remove punctuation from corpus'),
        click.option('--remove-digits', is_flag=True, help='Remove digits from corpus'),
        click.option('--normalize-whitespace', is_flag=True, help='Normalize whitespace in corpus'),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def _build_model(corpus, corpus_list, corpus_weights, ngram_size, stream,
                 lowercase, remove_punctuation, remove_digits, normalize_whitespace):
    """Load the corpus (or corpora) and build the n-gram model, reporting progress"""
    from markov_passgen.core.multi_corpus_manager import MultiCorpusManager
    from markov_passgen.transformers.text_cleaner import TextCleaner

    if not corpus and not corpus_list:
        click.echo("Error: Must specify either --corpus or --corpus-list", err=True)
        raise click.Abort()
    if corpus and corpus_list:
        click.echo("Error: Cannot use both --corpus and --corpus-list", err=True)
        raise click.Abort()

    cleaner = None
    if lowercase or remove_punctuation or remove_digits or normalize_whitespace:
        cleaner = TextCleaner(
            lowercase=lowercase,
            remove_punctuation=remove_punctuation,
            remove_digits=remove_digits,
            normalize_whitespace=normalize_whitespace
        )
        click.echo("Text preprocessing enabled")

    if corpus_list:
        click.echo(f"Loading {len(corpus_list)} corpus files...")
        weights = None
        if corpus_weights:
            try:
                weights = [float(w.strip()) for w in corpus_weights.split(',')]
            except ValueError:
                click.echo("Error: Invalid weight format. Use comma-separated numbers "
                           "(e.g., '1.0,2.0,1.5')", err=True)
                raise click.Abort() from None
            if len(weights) != len(corpus_list):
                click.echo(f"Error: Number of weights ({len(weights)}) must match "
                           f"number of corpora ({len(corpus_list)})", err=True)
                raise click.Abort()
            click.echo(f"Using corpus weights: {weights}")

        manager = MultiCorpusManager.from_files(list(corpus_list), weights=weights, cleaner=cleaner)
        for name, corpus_stats in manager.get_corpus_stats().items():
            click.echo(f"  {name}: {corpus_stats['char_count']} chars, {corpus_stats['word_count']} words, "
                       f"weight={corpus_stats['weight']}")

        # Merge the per-corpus models, each scaled to its weight's share
        click.echo(f"Building {ngram_size}-gram model...")
        model = manager.build_model(n=ngram_size, per_line=not stream)
    else:
        loader = CorpusLoader()
        click.echo(f"Loading corpus from {corpus}...")
        text = loader.load_from_file(corpus, cleaner=cleaner)
        if not loader.validate_corpus(text):
            click.echo("Error: Corpus must be at least 100 characters", err=True)
            raise click.Abort()
        stats = loader.get_corpus_stats()
        click.echo(f"Corpus loaded: {stats['char_count']} chars, {stats['word_count']} words")

        # One entry per line, unless --stream
        click.echo(f"Building {ngram_size}-gram model...")
        builder = NGramBuilder()
        model = builder.build(text, n=ngram_size) if stream else builder.build_lines(text, n=ngram_size)

    click.echo(f"Model built with {len(model)} n-grams")
    return model


@main.command()
@_corpus_options
@click.option('--output', required=True, type=click.Path(), help='Where to save the model (JSON)')
def train(corpus, corpus_list, corpus_weights, ngram_size, stream, lowercase, remove_punctuation,
          remove_digits, normalize_whitespace, output):
    """Build a model once and save it, for generate --model"""
    try:
        import json
        model = _build_model(corpus, corpus_list, corpus_weights, ngram_size, stream,
                             lowercase, remove_punctuation, remove_digits, normalize_whitespace)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(model, f)
        click.echo(f"Model saved to {output}")
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.command()
@_corpus_options
@click.option('--model', 'model_file', type=click.Path(exists=True),
              help='Use a model saved by train instead of a corpus')
@click.option('--count', default=100, help='Number of passwords to generate')
@click.option('--length', type=click.IntRange(min=1),
              help='Exact length of every candidate (default: lengths follow the corpus)')
@click.option('--min-length', type=click.IntRange(min=1), help='Shortest candidate to generate')
@click.option('--max-length', type=click.IntRange(min=1), help='Longest candidate to generate (default 64)')
@click.option('--require-digits', is_flag=True, help='Require at least one digit')
@click.option('--require-uppercase', is_flag=True, help='Require at least one uppercase letter')
@click.option('--require-lowercase', is_flag=True, help='Require at least one lowercase letter')
@click.option('--require-special', is_flag=True, help='Require at least one special character')
@click.option('--min-markov-bits', type=float,
              help='Keep candidates the model finds at least this surprising: total bits, -log2 P(candidate)')
@click.option('--min-entropy', type=float,
              help='Keep candidates whose average bits per character under the model is at least this (typically 1-4)')
@click.option('--seed-word', type=str, help='Seed word to start generation')
@click.option('--random-seed', type=int, help='Random seed for deterministic generation')
@click.option('--leet-speak', type=float, help='Apply leet speak transformation (0.0-1.0 intensity)')
@click.option('--case-variation', type=click.Choice(['random', 'alternating', 'capitalize']),
              help='Apply case variation')
@click.option('--output', default='wordlist.txt', help='Output file')
def generate(corpus, corpus_list, corpus_weights, ngram_size, stream, lowercase, remove_punctuation,
             remove_digits, normalize_whitespace, model_file, count, length, min_length, max_length,
             require_digits, require_uppercase, require_lowercase, require_special,
             min_markov_bits, min_entropy, seed_word, random_seed, leet_speak, case_variation, output):
    """Generate passwords from a corpus or a saved model"""
    try:
        from markov_passgen.filters.character_filter import CharacterFilter
        from markov_passgen.filters.filter_chain import FilterChain
        from markov_passgen.filters.length_filter import LengthFilter
        from markov_passgen.transformers.password_transformer import (
            CaseVariationTransformer,
            LeetSpeakTransformer,
            TransformerChain,
        )

        if model_file:
            if corpus or corpus_list:
                click.echo("Error: Use either --model or a corpus, not both", err=True)
                raise click.Abort()
            click.echo(f"Loading model from {model_file}...")
            model = NGramBuilder().load_model(model_file)
            if not model:
                click.echo("Error: The model file is empty", err=True)
                raise click.Abort()
            click.echo(f"Model loaded with {len(model)} n-grams")
        else:
            model = _build_model(corpus, corpus_list, corpus_weights, ngram_size, stream,
                                 lowercase, remove_punctuation, remove_digits, normalize_whitespace)

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

        if min_length and max_length and min_length > max_length:
            click.echo("Error: --min-length must not be larger than --max-length", err=True)
            raise click.Abort()

        # Filters run after transformations (leetspeak can add the digits a
        # filter requires). Length is part of generation; the length filter
        # only matters for stream-mode output, which ignores min/max.
        filter_chain = FilterChain()
        if (min_length or max_length) and length is None:
            filter_chain.add_filter(LengthFilter(min_length or 0, max_length or 1000))
        if require_digits or require_uppercase or require_lowercase or require_special:
            filter_chain.add_filter(CharacterFilter(
                require_digits=require_digits,
                require_uppercase=require_uppercase,
                require_lowercase=require_lowercase,
                require_special=require_special
            ))
        entropy_calc = None
        if min_entropy or min_markov_bits:
            from markov_passgen.core.entropy_calculator import EntropyCalculator
            entropy_calc = EntropyCalculator()

        # Generate in batches until enough candidates pass every filter
        click.echo(f"Generating {count} passwords...")
        passwords = []
        batch = max(count, 100)
        max_batches = 50
        for _ in range(max_batches):
            candidates = generator.generate(batch, length, seed=seed_word,
                                            min_length=min_length, max_length=max_length)
            if entropy_calc is not None and min_entropy:
                candidates = [c for c in candidates
                              if entropy_calc.calculate_markov_entropy(c, model) >= min_entropy]
            if entropy_calc is not None and min_markov_bits:
                candidates = [c for c in candidates
                              if entropy_calc.calculate_markov_bits(c, model) >= min_markov_bits]
            if transformer_chain:
                candidates = transformer_chain.transform_batch(candidates)
            if len(filter_chain):
                candidates = filter_chain.apply(candidates)
            passwords.extend(candidates)
            if len(passwords) >= count:
                break
        passwords = passwords[:count]

        if len(passwords) < count:
            click.echo(f"Warning: Only {len(passwords)} passwords meet the criteria "
                       f"after {max_batches * batch} attempts", err=True)

        # Write to output file
        with open(output, 'w', encoding='utf-8') as f:
            for password in passwords:
                f.write(password + '\n')

        click.echo(f"Successfully generated {len(passwords)} passwords to {output}")

    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


if __name__ == '__main__':
    main()
