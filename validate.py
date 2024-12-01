from embed import Embed


class Validate:
    def __init__(self, data, node_type):
        self.data = data
        self.embed = Embed(data, node_type)

    def validate_watermark(self, id_list, attributes):
        # Convert id_list to a set for fast membership checks
        id_set = set(str(key) for key in id_list)  # Use set to avoid duplicates and improve lookup speed

        # Iterate over each record in the list with its index (record number)
        for index, record in enumerate(self.data):
            # Ensure the record has a 'watermark_id'
            if 'company_id' in record:
                watermark_id = str(record['company_id'])
                if watermark_id in id_set:
                    record_hash, hashed_secret_int = self.embed.watermark_pseudo_node(record, watermark_id,
                                                                                      "company_id",
                                                                                      attributes)
                    if hashed_secret_int == id_list[watermark_id]:
                        return True
                else:
                    return False

    def validate_watermark_all(self, id_list, attributes):
        # Convert id_list to a set for fast membership checks
        id_set = set(str(key) for key in id_list)  # Use set to avoid duplicates and improve lookup speed
        pseudo_node_count = 0
        # Iterate over each record in the list with its index (record number)
        for index, record in enumerate(self.data):
            # Ensure the record has a 'watermark_id'
            if 'company_id' in record:
                watermark_id = str(record['company_id'])
                if watermark_id in id_set:
                    record_hash, hashed_secret_int = self.embed.watermark_pseudo_node(record, watermark_id,
                                                                                      "company_id",
                                                                                      attributes)
                    if hashed_secret_int == id_list[watermark_id]:
                        pseudo_node_count += 1

        return pseudo_node_count
