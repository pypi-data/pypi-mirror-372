import hashlib
import random

# def get_group_number(email):
#     if not email or email=='' or not isinstance(email, str):
#         return -1
#     # Use a 64-bit hash, similar to FarmHash in spirit
#     hash_value = int(hashlib.md5(email.lower().encode('utf-8')).hexdigest(), 16)
#     return hash_value % 100


def get_consistent_customer_number(email_address):
    """
    Generates a deterministic integer between 0 and 99 for a customer email.
    The email is normalized before hashing to ensure consistency.
    """
    if not email_address or email_address=='' or not isinstance(email_address, str):
        return -1
    # Step 1: Normalize the email address
    normalized_email = email_address.lower()
    
    # Step 2: Hash the normalized email using SHA-256
    sha256_hash = hashlib.sha256(normalized_email.encode('utf-8'))
    hex_digest = sha256_hash.hexdigest()
    
    # Step 3: Truncate the hex string and convert it to an integer
    truncated_hex = hex_digest[:15]
    hash_as_int = int(truncated_hex, 16)
    
    # Step 4: Apply the modulo operator to get a number from 0 to 99
    final_number = hash_as_int % 100
    
    return final_number


def generate_buckets(n, control_group, max_bucket=99, seed=None):
    """
    Generate `n` random bucket numbers between 0 and max_bucket (inclusive),
    excluding the values in control_group. Optionally set a random seed.
    
    Parameters:
        n (int)                : number of buckets to generate
        control_group (list)   : list of bucket numbers to exclude
        max_bucket (int)       : upper bound of bucket range (default = 99)
        seed (int or None)     : random seed for reproducibility (default = None)
    
    Returns:
        list: list of generated bucket numbers
    """
    if seed is not None:
        random.seed(seed)

    # build a list of eligible buckets
    eligible = [b for b in range(max_bucket + 1) if b not in control_group]

    if n > len(eligible):
        raise ValueError("n is larger than the number of available (eligible) buckets.")

    return sorted(random.sample(eligible, n))