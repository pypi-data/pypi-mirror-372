import GEOparse

def view_metadata_by_id():

    """
    Retrieve and display detailed metadata for any GEO accession (GSE, GDS, GPL). This function prompts the user to enter a GEO ID, fetches metadata
    using GEOparse, and prints all metadata fields in a readable format.

    Notes:
        - Interactive function: requires user input at runtime.
        - Does not return any value; outputs are printed directly to the console.
        - Suitable for retrieving metadata for any type of GEO dataset (GSE, GDS, GPL).

    User Input:
        - GEO accession ID (str): e.g., "GSE12345", "GDS67890", "GPL13579".
    
    Returns:
        None

    Example Usage:
        >>> metadata = geofetchr.view_metadata_by_id()
        >>> Print(metadata)

        output: 
        Enter a GEO ID (e.g., GSE12345, GDS67890, GPL13579): GSE4008

          **Metadata for GSE4008:**
        title: ['Genome-Wide Identification of Direct Targets of the Drosophila Retinal Determination Protein Eyeless']
        geo_accession: ['GSE4008']
        status: ['Public on Jan 11 2006']
        submission_date: ['Jan 10 2006']
        pubmed_id: ['16533912']
        summary: ['The discovery of direct downstream targets of transcription factors (TFs) is necessary for understanding the genetic mechanisms underlying complex, highly regulated processes such as development. ...']
        overall_design: ['biological triplicates were done for all samples']
        sample_id: []
    
    """

    geo_id = input("\nEnter a GEO ID (e.g., GSE12345, GDS67890, GPL13579): ").strip()
    if not geo_id:
        return
    try:
        geo = GEOparse.get_GEO(geo=geo_id, silent=False)
        print(f"\n🔹 **Metadata for {geo_id}:**")
        for key, value in geo.metadata.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error retrieving metadata: {e}")
        