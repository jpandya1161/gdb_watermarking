from embed import Embed


class Validate:
    def __init__(self, data, node_type, private_key):
        self.data = data
        self.embed = Embed(data, node_type, private_key=private_key)

    def validate_watermark(self, wm_id_dict, watermark_cover_field):
        # Convert id_list to a set for fast membership checks
        # id_set = set(str(key) for key in id_list)  # Use set to avoid duplicates and improve lookup speed

        # Iterate over each record in the list with its index (record number)
        for index, record in enumerate(self.data):
            attributes = [key for key, value in record.items() if isinstance(value, (int, float))]
            # print(attributes)
            # Ensure the record has a 'watermark_id'
            if watermark_cover_field in record:
                # print("cover in record")
                watermark_id = int(record[watermark_cover_field])
                if watermark_id in wm_id_dict.keys():
                    # print("key in wm secret")
                    _, hashed_secret_int = self.embed.watermark_pseudo_node(pseudo_node=record, watermark_identity=str(watermark_id),
                                                                                      watermark_id_field=watermark_cover_field, attributes=attributes, validate=True)
                    # print(f"Watermark id: {watermark_id}")
                    # print(attributes)
                    # print(record)
                    # print("BOTH HASHES")
                    # print(hashed_secret_int, wm_id_dict[watermark_id])
                    
                    if hashed_secret_int == wm_id_dict[watermark_id]:
                        return True
        
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
